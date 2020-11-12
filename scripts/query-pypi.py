#!/usr/bin/env python3
import os
import pathlib
import pprint
import sys
import tempfile
from contextlib import contextmanager

import httpx
import msgpack
import trio
from lxml import html
from tqdm import tqdm

DISABLE_TQDM = "CI" in os.environ
HEADERS = {"user-agent": "https://github.com/salt-extensions/salt-extensions-index"}
LOCAL_CACHE_PATH = pathlib.Path(
    os.environ.get("LOCAL_CACHE_PATH") or pathlib.Path(os.getcwd()).joinpath(".cache")
)
if not LOCAL_CACHE_PATH.is_dir():
    LOCAL_CACHE_PATH.mkdir(0o755)
PACKAGE_INFO_CACHE = LOCAL_CACHE_PATH / "packages-info"
if not PACKAGE_INFO_CACHE.is_dir():
    PACKAGE_INFO_CACHE.mkdir(0o755)

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
                progress.write(
                    f"The PyPi index server had {len(package_list)} packages. "
                    f"{len(new_packages)} were new. {len(old_packages)} were old and were deleted"
                )
                set_progress_description(progress, "Parsing HTML for packages complete")
    finally:
        progress.update()


async def collect_packages_information(session, index_info, limiter, progress):
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


async def download_package_info(session, package, package_info, limiter, progress):
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        headers = {}
        etag = package_info.get("etag")
        if etag:
            headers["If-None-Match"] = etag

        set_progress_description(progress, f"Querying info for {package}")
        req = await session.get(url, headers=headers, timeout=10)
        package_info["etag"] = req.headers.get("etag")
        if req.status_code == 304:
            set_progress_description(progress, f"No changes for {package}")
            # The package information has not changed:
            return
        if req.status_code != 200:
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
            if package.startswith(("salt-ext-", "salt-extension")):
                salt_extension = True
            elif (
                data["info"]["keywords"]
                and "salt-extension" in data["info"]["keywords"]
            ):
                salt_extension = True
            if salt_extension:
                package_info_cache = PACKAGE_INFO_CACHE / f"{package}.msgpack"
                package_info_cache.write_bytes(msgpack.packb(data))
        except Exception:
            pprint.pprint(data)
            raise
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
        return 0


if __name__ == "__main__":
    sys.exit(trio.run(main))
