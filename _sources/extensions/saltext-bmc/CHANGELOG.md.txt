The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 0.0.1 (2026-05-19)


### Changed

- The default backend is now ``auto`` instead of ``redfish``. Profiles that omit ``backend:`` will probe Redfish first and fall back to IPMI on TLS / connection / non-Redfish HTTP responses — so mixed fleets containing both modern (Redfish) and legacy (IPMI-only) hardware work without per-profile configuration. To preserve the previous fast-path behaviour on Redfish-only fleets, set ``backend: redfish`` explicitly to skip the probe.


### Fixed

- `bmc.get_system_info` on the IPMI backend now works on legacy BMCs. The previous implementation called `Command.get_fru()` and `Command.get_bmc_information()` — neither of which exist on `pyghmi.ipmi.command.Command`. The fix:

  - Calls pyghmi's actual API (`get_firmware()`) for BMC firmware version, plus a tolerant in-house FRU reader for the system FRU. Pyghmi's built-in FRU read starts at a 224-byte chunk size and only backs off on IPMI completion codes 0xC9 / 0xCA, leaving older BMCs (e.g. early HP iLO / Allegro RomPager-based BMCs) that return 0xC7 ("Request data length invalid") with no usable inventory. Our reader treats 0xC7 the same way pyghmi treats 0xC9 / 0xCA — halve the chunk and retry — then parses the bytes with pyghmi's own `FRU` class.
  - Recognises pyghmi's title-case FRU keys (`Manufacturer`, `Product name`, `Serial Number`, `Model`, `UUID`, `SKU`) in `_normalize_fru_flat`; snake-case keys are still accepted for backwards compatibility.
  - Returns `None` for fields the BMC does not expose rather than raising, matching the docstring promise. Each component (FRU, firmware, power) is queried independently.
