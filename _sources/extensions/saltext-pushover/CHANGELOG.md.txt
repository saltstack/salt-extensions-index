The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 2.0.0 (2026-03-17)


### Changed

- Stopped validating device names and sound names when posting a message since Pushover just ignores them. Invalid user names still result in an error. [#20](https://github.com/salt-extensions/saltext-pushover/issues/20)
- BREAKING: Reordered parameters to `pushover_notify.post_message` to make it explicit `message` is the only absolutely required parameter [#22](https://github.com/salt-extensions/saltext-pushover/issues/22)
- Made query utility accept API paths instead of internally defined identifiers
- Made query utility communicate errors through exceptions to improve reliability and code quality
- Made query utility return decoded API responses only


### Fixed

- Removed unused `api_version` parameter, made query util function respect `token` parameter, made state module respect `sound` parameter [#21](https://github.com/salt-extensions/saltext-pushover/issues/21)

## 1.0.1 (2024-11-03)


### Fixed

- Fixed default parameter handling [#17](https://github.com/salt-extensions/saltext-pushover/issues/17)
- Made state module respect `user` from config [#18](https://github.com/salt-extensions/saltext-pushover/issues/18)


## v1.0.0 (2024-05-28)

First release with code extracted from Salt core.
No significant changes.
