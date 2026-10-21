The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 1.2.3 (2026-02-08)


### Fixed

- Fixed a crash in the elasticsearch9 returner when `states_order_output` is enabled (dict modified during iteration). Fixed `event_return()` to index each event individually instead of only the last one. Fixed `search()` in both elasticsearch8 and elasticsearch9 modules to parse JSON string `body` arguments before calling `.get()`. [#22](https://github.com/salt-extensions/saltext-elasticsearch/issues/22)

## 1.2.1 (2024-01-17)


### Added

- Fixed towncrier config and changelog to release [#6](https://github.com/salt-extensions/saltext-elasticsearch/pull/6)

## [1.1.1](https://github.com/cesan3/salt-ext-elasticsearch/compare/1.1.0...1.1.1) - 2023-11-17
- fix: pass correct id attribute name by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/20

## [1.1.0](https://github.com/cesan3/salt-ext-elasticsearch/compare/1.0.0...1.1.0) - 2023-11-17
- Fix returner for ES8 by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/18

## [1.0.0](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.8...1.0.0) - 2023-11-08
- Merge upstream by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/16

## [0.0.8](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.7...0.0.8) - 2023-11-06
- fix: add elasticsearch returner by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/14

## [0.0.7](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.6...0.0.7) - 2023-11-06
- Revert "fix: obsoletes saltext.elasticsearch8" by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/12

## [0.0.6](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.5...0.0.6) - 2023-11-06
- fix: obsoletes saltext.elasticsearch8 by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/10

## [0.0.5](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.4...0.0.5) - 2023-11-06
- fix: add flush_synced method to ES6 module by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/8

## [0.0.4](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.3...0.0.4) - 2023-11-06
- fix: update test workflow by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/6

## [0.0.3](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.2...0.0.3) - 2023-11-06
- Update release.yml by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/4

## [0.0.2](https://github.com/cesan3/salt-ext-elasticsearch/compare/0.0.1...0.0.2) - 2023-11-06
- feat: Adding elasticsearch extension module by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/1
- fix: update README by @cesan3 in https://github.com/cesan3/salt-ext-elasticsearch/pull/2

## [0.0.1](https://github.com/cesan3/salt-ext-elasticsearch/commits/0.0.1) - 2023-11-04
