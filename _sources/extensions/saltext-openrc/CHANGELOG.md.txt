The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 0.2.1 (2026-10-29)


### Changed

- Removed direct dependency on Salt, it is expected to be provided by the environment instead. You can still request it explicitly via the `salt` extra (`pip install saltext-openrc[salt]`)

## 0.2.0 (2026-09-17)


### Added

Support openrc's `zap` call.

## 0.1.0 (2026-09-16)


### Added

- OpenRC ``service`` execution module, extracted from ``saltext-alpine``.
