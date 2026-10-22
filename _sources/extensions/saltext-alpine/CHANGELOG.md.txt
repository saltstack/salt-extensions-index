The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 1.0.4 (2026-10-21)


### Fixed

- Add an Alpine-specific ``system`` module that reimplements ``reboot``, ``shutdown``, ``poweroff``, and ``halt`` on top of BusyBox. This fixes ``FileNotFoundError: 'shutdown'`` when calling ``system.reboot`` and friends on Alpine, where no ``shutdown`` binary is present.

## 1.0.3 (2026-10-05)

Remove openrc module, and now depend on saltext-openrc


## 1.0.2 (2026-08-26)

No significant changes.


## 1.0.1 (2026-08-26)

- Fix saltext entrypoint


## 1.0.0 (2026-05-22)

- Migrated apkpkg from legacy repo and merged into broader Alpine support saltext
- Added openrc service support
