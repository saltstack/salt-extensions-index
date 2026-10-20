#!/usr/bin/env python3
"""Collect released Salt extension documentation into the central Sphinx site."""

import datetime
import io
import json
import os
import pathlib
import re
import shutil
import tarfile
import urllib.error
import urllib.parse
import urllib.request

from packaging.version import InvalidVersion, Version

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXTENSIONS_DIR = DOCS / "extensions"
API = "https://api.github.com"
ORG = os.environ.get("GITHUB_ORG", "salt-extensions")
TOKEN = os.environ.get("GITHUB_TOKEN")
NON_EXTENSION_REPOSITORIES = {
    "central-artifacts",
    "community",
    "community-extensions-holding",
    "extension_migration",
    ".github",
    "salt-extension-copier",
    "salt-extension-migrate",
    "salt-extensions-index",
}


def is_extension_repository(repo):
    name = repo["name"]
    topics = set(repo.get("topics", []))
    return (
        name.startswith(("saltext-", "salt-ext-"))
        or "salt-extension" in topics
        or "saltstack-extension" in topics
        or name == "salt-describe"
    )


def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "salt-extensions-index"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def repositories():
    page = 1
    while True:
        url = f"{API}/orgs/{ORG}/repos?per_page=100&page={page}&type=public"
        batch = get_json(url)
        yield from (
            repo
            for repo in batch
            if repo["name"] not in NON_EXTENSION_REPOSITORIES
            and is_extension_repository(repo)
        )
        if len(batch) < 100:
            break
        page += 1


def release_for(repo):
    base = f"{API}/repos/{ORG}/{repo['name']}"
    try:
        release = get_json(f"{base}/releases/latest")
        return release["tag_name"], release.get("published_at", "")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    tags = []
    page = 1
    while True:
        batch = get_json(f"{base}/tags?per_page=100&page={page}")
        tags.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    if not tags:
        return "", ""
    # Prefer the greatest semantic version; for non-versioned tags use newest commit date.
    versions = []
    for tag in tags:
        candidate = tag["name"].lstrip("v")
        try:
            versions.append((Version(candidate), tag))
        except InvalidVersion:
            continue
    if versions:
        tag = max(versions, key=lambda item: item[0])[1]
        return tag["name"], ""
    tag = max(tags, key=lambda item: item.get("commit", {}).get("commit", {}).get("committer", {}).get("date", ""))
    return tag["name"], ""


def safe_member_path(name, prefix):
    path = pathlib.PurePosixPath(name)
    parts = path.parts
    if len(parts) < 2 or parts[1] != prefix or ".." in parts:
        return None
    return pathlib.PurePosixPath(*parts[2:])


def download_docs(repo, tag, destination):
    ref = urllib.parse.quote(tag, safe="")
    url = f"https://codeload.github.com/{ORG}/{repo['name']}/tar.gz/refs/tags/{ref}"
    request = urllib.request.Request(url, headers={"User-Agent": "salt-extensions-index"})
    with urllib.request.urlopen(request, timeout=120) as response:
        archive = tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz")
        copied = 0
        api_references = set()
        for member in archive.getmembers():
            rel = safe_member_path(member.name, "docs")
            if rel is None or not rel.parts or not member.isfile():
                continue
            if len(rel.parts) == 3 and rel.parts[0] == "ref" and rel.parts[2] == "index.rst":
                api_references.add(rel.parts[1])
            if rel.parts[0] == "ref" or rel.as_posix() in ("index.rst", "index.md"):
                continue
            target = destination / "docs" / pathlib.Path(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source:
                contents = source.read()
                if target.name == "changelog.md":
                    text = contents.decode("utf-8")
                    text = re.sub(
                        r"(?ms)^```\{towncrier-draft-entries\}\s*```\s*", "", text
                    )
                    contents = text.encode("utf-8")
                target.write_bytes(contents)
                copied += 1
        root_name = archive.getmembers()[0].name.split("/")[0]
        for filename in ("CHANGELOG.md", "README.md"):
            member = next(
                (
                    item
                    for item in archive.getmembers()
                    if item.name == f"{root_name}/{filename}" and item.isfile()
                ),
                None,
            )
            if member:
                source = archive.extractfile(member)
                if source:
                    destination.mkdir(parents=True, exist_ok=True)
                    (destination / filename).write_bytes(source.read())
        docs_root = destination / "docs"
        if docs_root.is_dir():
            sources = sorted(
                path
                for path in docs_root.rglob("*")
                if path.is_file()
                and path.suffix in (".rst", ".md")
                and path.name not in ("sitevars.rst", "index.rst", "index.md")
                and "ref" not in path.relative_to(docs_root).parts
            )
            lines = [
                repo["name"],
                "=" * len(repo["name"]),
                "",
                repo.get("description") or "Salt extension documentation",
                "",
                f"Release: ``{tag}``" if tag else "No tagged release is available.",
                "",
                ".. toctree::",
                "   :maxdepth: 2",
                "   :caption: Documentation",
                "",
            ]
            lines.extend(
                f"   docs/{path.relative_to(docs_root).with_suffix('').as_posix()}"
                for path in sources
            )
            if api_references:
                lines.extend(["", "Provided Modules", "----------------", ""])
                docs_url = f"https://salt-extensions.github.io/{repo['name']}/ref"
                if "modules" in api_references:
                    lines.append(f"* `Execution modules <{docs_url}/modules/index.html>`_")
                if "states" in api_references:
                    lines.append(f"* `State modules <{docs_url}/states/index.html>`_")
            (destination / "index.rst").write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif (destination / "README.md").is_file():
            copied = 1
        return copied


def rst_escape(value):
    return value.replace("`", "\\`")


def main():
    repo_list = list(repositories())
    (DOCS / "extensions-index.rst").unlink(missing_ok=True)
    if EXTENSIONS_DIR.exists():
        shutil.rmtree(EXTENSIONS_DIR)
    EXTENSIONS_DIR.mkdir(parents=True)
    entries = []
    errors = []
    for repo in repo_list:
        name = repo["name"]
        slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
        try:
            tag, released = release_for(repo)
            count = download_docs(repo, tag, EXTENSIONS_DIR / slug) if tag else 0
            entries.append(
                (
                    name,
                    slug,
                    tag,
                    released,
                    count,
                    repo["html_url"],
                    repo.get("description") or "No description provided.",
                )
            )
            print(f"{name}: {tag} ({count} documentation files)")
        except Exception as exc:  # Keep one broken repository from hiding all other docs.
            errors.append(f"{name}: {exc}")
            print(f"WARNING: {name}: {exc}")

    lines = [
        "Salt Extensions", "===============", "",
        "A catalog of public Salt extension repositories. Documentation is collected nightly from each "
        "repository's latest release. "
        "If a repository has no published GitHub release, its highest version tag is used. Repositories "
        "without tags are listed without imported documentation. The collected source files are rendered with this "
        "site's Sphinx configuration; extension-specific configuration code is not executed.", "",
        f"Last generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "",
        ".. raw:: html", "", '   <label for="extension-filter">Filter extensions</label>',
        '   <input id="extension-filter" type="search" placeholder="Name or description" autocomplete="off">',
        '   <span id="extension-count" aria-live="polite"></span>', "",
        ".. list-table::", "   :class: extension-index", "   :header-rows: 1", "   :widths: 18 40 15 14 15", "",
        "   * - Extension", "     - Description", "     - Latest release", "     - Released", "     - Documentation",
    ]
    for name, slug, tag, released, count, url, description in sorted(entries):
        extension_docs = EXTENSIONS_DIR / slug
        doc_index = next(
            (
                path
                for path in (
                    extension_docs / "index.rst",
                    extension_docs / "index.md",
                    extension_docs / "README.md",
                )
                if path.exists()
            ),
            None,
        )
        if doc_index:
            doc_target = doc_index.relative_to(DOCS).with_suffix("").as_posix()
            doc_link = f":doc:`Browse docs <{doc_target}>`"
        else:
            doc_link = "No published documentation"
        if tag:
            tag_url = f"https://github.com/{ORG}/{name}/tree/{urllib.parse.quote(tag, safe='/')}"
            release_label = f"`{rst_escape(tag)} <{tag_url}>`_"
        else:
            release_label = "No release tag"
        if not doc_index and count:
            docs_url = f"https://github.com/{ORG}/{name}/tree/{urllib.parse.quote(tag, safe='/')}/docs" if tag else url
            doc_link = f"`Browse source docs <{docs_url}>`_"
        lines.extend([
            f"   * - `{name} <{url}>`_",
            f"     - {description.replace(chr(10), ' ').strip()}",
            f"     - {release_label}",
            f"     - {released[:10] if released else '—'}",
            f"     - {doc_link}",
        ])
    if not entries:
        lines.extend(["", "No extension repositories were found."])
    if errors:
        lines.extend(["Collection warnings", "-------------------", ""])
        lines.extend(f"* {error}" for error in errors)
        lines.append("")
    (DOCS / "index.rst").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        pathlib.Path(os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/extensions-docs-summary.md")).write_text(
            "## Documentation collection warnings\n\n" + "\n".join(f"- {error}" for error in errors) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
