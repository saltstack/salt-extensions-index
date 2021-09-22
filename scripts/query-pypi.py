#!/usr/bin/env python3
import functools
import os
import pathlib
import pprint
import sys
import tempfile
import traceback
from contextlib import contextmanager

import httpx
import msgpack
import trio
from lxml import html
from tqdm import tqdm

DISABLE_TQDM = "CI" in os.environ
HEADERS = {"user-agent": "https://github.com/salt-extensions/salt-extensions-index"}

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
LOCAL_CACHE_PATH = pathlib.Path(
    os.environ.get("LOCAL_CACHE_PATH") or REPO_ROOT.joinpath(".cache")
)
if not LOCAL_CACHE_PATH.is_dir():
    LOCAL_CACHE_PATH.mkdir(0o755)
PACKAGE_INFO_CACHE = LOCAL_CACHE_PATH / "packages-info"
if not PACKAGE_INFO_CACHE.is_dir():
    PACKAGE_INFO_CACHE.mkdir(0o755)
STATE_DIR = REPO_ROOT / ".state"

KNOWN_SALT_EXTENSIONS = {
    "salt-cumulus",
    "salt-nornir",
    "salt-os10",
    "salt-ttp",
    "saltext.vmware",
}
KNOWN_NOT_SALT_EXTENSIONS = {
    "salt-extension",
    "salt-ext-tidx1",
    "salt-tidx2-extension",
}


print(f"Local Cache Path: {LOCAL_CACHE_PATH}", file=sys.stderr, flush=True)

if sys.version_info < (3, 7):
    print("This script is meant to only run on Py3.7+", file=sys.stderr, flush=True)


def set_progress_description(progress, message):
    progress.set_description(f"{message: <60}")


@contextmanager
def get_index_info(progress):
    local_pypi_index_info = LOCAL_CACHE_PATH / "pypi-index.msgpack"
    set_progress_description(progress, "Loading cache")
    if local_pypi_index_info.exists():
        index_info = msgpack.unpackb(local_pypi_index_info.read_bytes())
    else:
        index_info = {"packages": {}}
    progress.update()
    try:
        yield index_info
    finally:
        set_progress_description(progress, "Saving cache")
        local_pypi_index_info.write_bytes(msgpack.packb(index_info))
        progress.update()


async def download_pypi_simple_index(session, index_info, limiter, progress):
    try:
        async with limiter:
            headers = {}
            etag = index_info.get("etag")
            if etag:
                headers["If-None-Match"] = etag

            set_progress_description(progress, "Querying packages from PyPi")
            with tempfile.NamedTemporaryFile() as download_file:
                async with session.stream(
                    "GET", "https://pypi.org/simple/", headers=headers
                ) as response:

                    if response.status_code == 304:
                        # There are no new packages
                        progress.write("There are no new packages")
                        return

                    if response.status_code != 200:
                        progress.write(
                            "Failed to download the PyPi index. Status Code: {request.status_code}"
                        )
                        return
                    total = int(response.headers["Content-Length"])

                    with tqdm(
                        total=total,
                        unit_scale=True,
                        unit_divisor=1024,
                        unit="B",
                        disable=DISABLE_TQDM,
                    ) as dprogress:
                        dprogress.set_description("Downloading PyPi simple index")
                        num_bytes_downloaded = response.num_bytes_downloaded
                        async for chunk in response.aiter_bytes():
                            download_file.write(chunk)
                            dprogress.update(
                                response.num_bytes_downloaded - num_bytes_downloaded
                            )
                            num_bytes_downloaded = response.num_bytes_downloaded
                        dprogress.set_description(
                            "Downloading PyPi simple index complete."
                        )

                index_info["etag"] = response.headers.get("etag")
                STATE_DIR.joinpath("pypi-index-etag").write_text(index_info["etag"])

                set_progress_description(
                    progress, "Querying packages from PyPi completed"
                )

                set_progress_description(progress, "Parsing HTML for packages")
                tree = html.fromstring(pathlib.Path(download_file.name).read_text())
                old_packages = set(index_info["packages"])
                new_packages = set()
                package_list = index_info["packages"]
                for package in tree.xpath("//a/text()"):
                    if package in old_packages:
                        old_packages.remove(package)
                    if package not in package_list:
                        new_packages.add(package)
                        package_list[package] = {}
                if old_packages:
                    progress.write(
                        f"Removing the following old packages from "
                        f"cache: {', '.join(old_packages)}"
                    )
                    for package in old_packages:
                        package_list.pop(package)
                        package_info_cache = PACKAGE_INFO_CACHE / f"{package}.msgpack"
                        if package_info_cache.exists():
                            package_info_cache.unlink()
                progress.write(
                    f"The PyPi index server had {len(package_list)} packages. "
                    f"{len(new_packages)} were new. {len(old_packages)} were old and were deleted"
                )
                if len(new_packages) <= 100:
                    progress.write("New packages:")
                    for package in new_packages:
                        progress.write(f" * {package}")
                set_progress_description(progress, "Parsing HTML for packages complete")
    finally:
        progress.update()


async def collect_packages_information(session, index_info, limiter, progress):
    processed = 0
    muted_processed_iterations = 1500
    try:
        async with trio.open_nursery() as nursery:
            for package in index_info["packages"]:
                async with limiter:
                    nursery.start_soon(
                        download_package_info,
                        session,
                        package,
                        index_info["packages"][package],
                        limiter,
                        progress,
                    )
                if DISABLE_TQDM:
                    processed += 1
                    muted_processed_iterations -= 1
                    if not muted_processed_iterations:
                        muted_processed_iterations = 1500
                        progress.write(
                            f"Processed {processed} of {len(index_info['packages'])}"
                        )
    finally:
        if DISABLE_TQDM:
            progress.write(f"Processed {processed} of {len(index_info['packages'])}")
        # Store the known extensions hash into state to trigger a cache hit/miss/update
        # on the Github Actions CI pipeline
        extensions = {}
        for path in PACKAGE_INFO_CACHE.glob("*.msgpack"):
            extension_data = msgpack.unpackb(path.read_bytes())
            extensions[path.stem] = extension_data
        extensions_hash = functools.reduce(
            lambda x, y: x ^ y,
            [hash((key, repr(value))) for (key, value) in sorted(extensions.items())],
        )
        STATE_DIR.joinpath("known-extensions-hash").write_text(f"{extensions_hash}")


async def download_package_info(session, package, package_info, limiter, progress):
    try:
        if package_info.get("not-found"):
            return
        url = f"https://pypi.org/pypi/{package}/json"
        headers = {}
        etag = package_info.get("etag")
        if etag:
            headers["If-None-Match"] = etag

        set_progress_description(progress, f"Querying info for {package}")
        try:
            req = await session.get(url, headers=headers, timeout=15)
        except (httpx.TimeoutException, trio.ClosedResourceError) as exc:
            progress.write(f"Failed to query info for {package}: {exc}")
            return
        package_info["etag"] = req.headers.get("etag")
        if req.status_code == 304:
            set_progress_description(progress, f"No changes for {package}")
            # The package information has not changed:
            return
        if req.status_code != 200:
            if req.status_code == 404:
                package_info["not-found"] = True
            progress.write(
                f"Failed to query info for {package}. Status code: {req.status_code}"
            )
            return

        data = req.json()
        if not data:
            progress.write(
                "Failed to get JSON data back. Got:\n>>>>>>\n{req.text}\n<<<<<<"
            )
            return
        try:
            salt_extension = False
            if package in KNOWN_SALT_EXTENSIONS:
                salt_extension = True
                progress.write(f"{package} is a known salt-extension")
            elif package not in KNOWN_NOT_SALT_EXTENSIONS:
                if package.startswith(("salt-ext-", "saltext-", "saltext.")):
                    salt_extension = True
                    progress.write(
                        f"{package} was detected as a salt-extension from it's name"
                    )
                elif (
                    data["info"]["keywords"]
                    and "salt-extension" in data["info"]["keywords"]
                ):
                    salt_extension = True
                    progress.write(
                        f"{package} was detected as a salt-extension because of it's keywords"
                    )
            if salt_extension:
                package_info_cache = PACKAGE_INFO_CACHE / f"{package}.msgpack"
                package_info_cache.write_bytes(msgpack.packb(data))
        except Exception:
            progress.write(traceback.format_exc())
            progress.write("Data:\n{}".format(pprint.pformat(data)))
    finally:
        progress.update()


async def main():
    timeout = 120 * 60  # move on after 2 hours
    progress = tqdm(
        total=sys.maxsize,
        unit="pkg",
        unit_scale=True,
        desc=f"{' ' * 60} :",
        disable=DISABLE_TQDM,
    )
    with progress:
        with get_index_info(progress) as index_info:
            concurrency = 1000
            limiter = trio.CapacityLimiter(concurrency)
            with trio.move_on_after(timeout) as cancel_scope:
                limits = httpx.Limits(
                    max_keepalive_connections=5, max_connections=concurrency
                )
                async with httpx.AsyncClient(
                    limits=limits, http2=True, headers=HEADERS
                ) as session:
                    await download_pypi_simple_index(
                        session, index_info, limiter, progress
                    )
                    if DISABLE_TQDM is False:
                        # We can't reset tqdm if it's disabled
                        progress.reset(total=len(index_info["packages"]))
                    await collect_packages_information(
                        session, index_info, limiter, progress
                    )
        if cancel_scope.cancelled_caught:
            progress.write(f"The script timmed out after {timeout} minutes")
            return 1
        progress.write("Detected Salt Extensions:")
        for path in PACKAGE_INFO_CACHE.glob("*.msgpack"):
            progress.write(f" * {path.stem}")
        return 0


if __name__ == "__main__":
    sys.exit(trio.run(main))
