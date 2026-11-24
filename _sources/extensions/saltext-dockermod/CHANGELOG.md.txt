The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 0.1.4 (2026-11-23)


### Fixed

- Do not delete already existing composefile when editing it fails. [#18](https://github.com/salt-extensions/saltext-dockermod/issues/18)
- Use extension's own copy of dockermod utils (``saltext.dockermod.utils.dockermod``) instead of Salt's ``salt.utils.dockermod``. [#19](https://github.com/salt-extensions/saltext-dockermod/issues/19)
- Fixed ``docker_network.present`` reporting spurious changes and recreating a network on every run when a ``subnet`` was specified without a ``gateway``. Docker auto-assigns the subnet's first host address as the gateway and reports it on inspect, while Salt's desired config omits the key entirely; ``docker.compare_networks`` now ignores a one-sided gateway only when it matches that auto-assigned default, so an explicitly added, removed, or changed gateway is still detected as a real change. [#22](https://github.com/salt-extensions/saltext-dockermod/issues/22)
- Fix `docker_container.running` destroying the original container on the
  `force=True` / `skip_comparison` path by passing the temp container's dict
  instead of its name to `_replace`. `docker.rename` then failed after
  `docker.rm` had already removed the original, leaving the minion with the
  temp container stranded under its generated name. `_replace` now receives
  `temp_container_name` on both call sites, matching the non-force path. [#25](https://github.com/salt-extensions/saltext-dockermod/issues/25)
- Fix ``docker_network.present`` not restoring a container's IPv6 address when reconnecting it to a recreated network, due to a typo in the ``IPv6Address`` key.
- Fixed ``docker_container.running`` leaking the anonymous volumes of the temporary container it creates to compare against an existing container, one per run for images that declare a ``VOLUME``.
- Fixed missing `compare_networks.compare_networks` ignore
  docstring, which omitted the `Status` key

## 0.1.3 (2026-09-21)

No significant changes.


## 0.1.2 (2026-09-18)


### Fixed

- Add docker source files that were missed when creating the dockermod extension. [#6](https://github.com/salt-extensions/saltext-dockermod/issues/6)

## v0.1.1 (2026-03-05)

No significant changes.


## v0.1.0 (2026-03-04)


### Fixed

- Backport https://github.com/saltstack/salt/pull/68270 to fix the failing tests. [#3](https://github.com/salt-extensions/saltext-dockermod/pull/3)
