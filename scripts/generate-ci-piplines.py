#!/usr/bin/env python3
import os
import pathlib
import sys

import msgpack
from jinja2 import Template
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

BLACKLISTED_EXTENSIONS = {"salt-extension"}

print(f"Local Cache Path: {LOCAL_CACHE_PATH}", file=sys.stderr, flush=True)

if sys.version_info < (3, 7):
    print("This script is meant to only run on Py3.7+", file=sys.stderr, flush=True)


def set_progress_description(progress, message):
    progress.set_description(f"{message: <60}")


def collect_extensions_info():
    packages = {}
    for path in sorted(PACKAGE_INFO_CACHE.glob("*.msgpack")):
        if path.stem in BLACKLISTED_EXTENSIONS:
            continue
        package_data = msgpack.unpackb(path.read_bytes())
        package = package_data["info"]["name"]
        for urlinfo in package_data["urls"]:
            if urlinfo["packagetype"] == "sdist":
                url = urlinfo["url"]
                break

        packages[package] = url
    return packages


def main():
    workflow = REPO_ROOT / ".github" / "workflows" / "test-extensions.yml"
    content = (
        REPO_ROOT / ".github" / "workflows" / "templates" / "generate-index-base.yml"
    ).read_text()
    common_context = {
        "salt_versions": ["3001.3", "3002.1"],
        "python_versions": ["3.5", "3.6", "3.7", "3.8"],
    }
    platform_templates = (
        REPO_ROOT / ".github" / "workflows" / "templates" / "linux.yml.j2",
        REPO_ROOT / ".github" / "workflows" / "templates" / "macos.yml.j2",
        REPO_ROOT / ".github" / "workflows" / "templates" / "windows.yml.j2",
    )
    packages = collect_extensions_info()
    progress = tqdm(
        total=len(packages),
        unit="pkg",
        unit_scale=True,
        desc=f"{' ' * 60} :",
        disable=DISABLE_TQDM,
    )
    with progress:
        needs = []
        for package, url in packages.items():
            set_progress_description(progress, f"Processing {package}")
            context = common_context.copy()
            context["package"] = package
            context["package_url"] = url
            for template_path in platform_templates:
                content += Template(template_path.read_text()).render(**context)
            for platform in ("Linux", "macOS", "Windows"):
                needs.append(f"{package}-{platform}")
            progress.update()
        generate_extensions_index = (
            REPO_ROOT / ".github" / "workflows" / "templates" / "generate-index.yml.j2"
        )
        set_progress_description(progress, "Writing workflow")
        content += Template(generate_extensions_index.read_text()).render(needs=needs)
        workflow.write_text(content.rstrip() + "\n")
    progress.write("Complete")
    return 0


if __name__ == "__main__":
    exitcode = 0
    try:
        main()
    except Exception:
        exitcode = 1
        raise
    finally:
        sys.exit(exitcode)
