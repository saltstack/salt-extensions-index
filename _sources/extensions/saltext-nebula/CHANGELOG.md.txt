The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 1.2.0 (2026-09-08)


### Added

- Added a ``nebula_ipam`` external pillar that dynamically allocates a stable Nebula overlay IP to each minion and injects it at ``nebula:hosts:<minion_id>:ip``, so a node can join the mesh without a hand-written address. Allocations are persisted in a SQLite database on the master (allocate-once, read-through), respect static host IPs, lighthouse addresses and operator ``reserve`` entries, and are serialized so concurrent pillar compilations cannot assign the same address twice. New ``nebula.ipam_list``, ``nebula.ipam_show`` and ``nebula.ipam_release`` runner functions manage the allocation store.

## 1.1.0 (2026-06-30)

### Changed

- Lighthouse nodes now pin ``listen.port`` to ``lighthouse_port`` by default instead of inheriting the global ``listen_port`` (which is typically ``0``/ephemeral and correct only for roaming nodes). A lighthouse on an ephemeral port is unreachable because every node's ``static_host_map`` targets ``lighthouse_port``. A new per-host ``listen_port`` key overrides this for either lighthouses or regular nodes.

### Fixed

- Corrected the ``build_config`` docstring, which claimed non-firewall dict settings were "deep merged" when ``remote_allow_list`` was in fact a shallow per-key merge. The docstring now documents the actual per-section merge semantics. The previously-unused ``_deep_merge`` helper is now used for the config-section overrides.

### Added

- The relay role can now be configured independently of the lighthouse role. A per-host ``is_relay`` flag overrides the default (``am_relay`` = ``is_lighthouse``), so a NAT'd lighthouse can stop acting as a relay or a well-connected regular node can become one. A lighthouse entry may set ``relay: false`` to be excluded from the relay list other nodes use while remaining a discovery lighthouse, and an explicit per-host or common ``relays`` list replaces the lighthouse-derived set entirely. Previously every lighthouse was forced to be a relay for the whole mesh with no opt-out.
- Hosts may now define a ``static_host_map`` in pillar (per-host or common) that is merged onto the map derived from ``lighthouses``. An entry replaces the derived endpoint list for a matching overlay IP or adds a new one, so a node co-located with a lighthouse can reach it over a local/bridge address instead of the globally derived public endpoint.
- The ``tun``, ``punchy``, ``logging`` and ``conntrack`` config sections, previously hardcoded, can now be overridden from pillar (common or per-host); overrides are deep-merged onto the defaults, so only the keys you set change. An optional top-level ``cipher`` may also be set (it must be identical on every node). The dedicated host-level ``unsafe_routes`` key is unchanged and takes precedence over any ``tun`` override.
- ``build_config`` now logs a warning when a host's pillar entry contains an unrecognized key (a typo, or a block indented at the wrong level), and when a Nebula config-section name such as ``firewall`` appears as a hostname under ``hosts:`` (the classic "indented one level too shallow" mistake, which silently leaves the intended host on defaults). These conditions previously failed silently.
- Added a ``nebula.show_config`` runner that renders the Nebula configuration a target minion would receive, computed from that minion's pillar on the master (via ``pillar.show_pillar``) without contacting the minion. It produces the same output as ``nebula.build_config`` and is useful for previewing or diffing a node's config, and for rendering (and writing) a single master's own Nebula config locally instead of standing up a second master to highstate it.

## 1.0.2 (2026-06-29)

- Added configuration handling for multiple lighthouses, including support for IPv6 and Dual-Stack deployments. (Thanks to @krombel!)

## 1.0.1 (2026-03-14)

- Added configuration handling for the built in lighthouse DNS server
- Added configuration handling for the built in lighthouse SSHD server

## 1.0.0 (2026-03-05)

- Initial release of saltext-nebula
