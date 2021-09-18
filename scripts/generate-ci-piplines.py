#!/usr/bin/env python3
import os
import pathlib
import sys

import github
import msgpack
import packaging.version
from jinja2 import Template
from slugify import slugify
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


def get_lastest_major_releases(progress, count=3):
    # This logic might have to change because the order of tags seems to be by creation time
    set_progress_description(progress, "Searching for latest salt releases...")
    gh = github.Github(login_or_token=os.environ.get("GITHUB_TOKEN") or None)
    repo = gh.get_repo("saltstack/salt")
    releases = []
    last_version = None
    for tag in repo.get_tags():
        if len(releases) == count:
            break
        version = packaging.version.parse(tag.name)
        try:
            if version.major < 3000:
                # Don't test versions of salt older than 3000
                continue
        except AttributeError:
            progress.write(f"Failed to parse tag {tag}")
            continue
        if last_version is None:
            last_version = version
            releases.append(tag.name)
            continue
        if version.major == last_version.major:
            continue
        last_version = version
        releases.append(tag.name)
    progress.write(f"Found the folowing salt releases: {', '.join(releases)}")
    return releases


def collect_extensions_info():
    packages = {}
    for path in sorted(PACKAGE_INFO_CACHE.glob("*.msgpack")):
        url = None
        if path.stem in BLACKLISTED_EXTENSIONS:
            continue
        package_data = msgpack.unpackb(path.read_bytes())
        package = package_data["info"]["name"]
        for urlinfo in package_data["urls"]:
            if urlinfo["packagetype"] == "sdist":
                url = urlinfo["url"]
                break

        if url is not None:
            packages[package] = url
    return packages


def main():
    workflow = REPO_ROOT / ".github" / "workflows" / "test-extensions.yml"
    content = (
        REPO_ROOT / ".github" / "workflows" / "templates" / "generate-index-base.yml"
    ).read_text()
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
    try:
        salt_versions = get_lastest_major_releases(progress)
    except Exception as exc:
        progress.write(f"Failed to get latest salt releases: {exc}")
        return 1
    common_context = {
        "salt_versions": salt_versions,
        "python_versions": ["3.5", "3.6", "3.7", "3.8", "3.9"],
    }
    with progress:
        needs = []
        for package, url in packages.items():
            set_progress_description(progress, f"Processing {package}")
            context = common_context.copy()
            slug = slugify(package)
            context["slug"] = slug
            context["package"] = package
            context["package_url"] = url
            for template_path in platform_templates:
                content += Template(template_path.read_text()).render(**context)
            for platform in ("linux", "macos", "windows"):
                needs.append(f"{slug}-{platform}")
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
