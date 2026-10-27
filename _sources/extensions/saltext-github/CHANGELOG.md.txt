The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 1.1.0 (2026-10-26)


### Removed

- Removed the unauthenticated `get_user_pubkeys` helper from `saltext.github.utils.github`. It ignored the configured {ghconf}`api_url`, relied on `salt.utils.http` and was not exposed in any module


### Deprecated

- Deprecated all current functions of the {py:mod}`github execution module <saltext.github.modules.github>` as well as the {py:mod}`github state module <saltext.github.states.github>`. Use the corresponding functions of the new {py:mod}`github_org <saltext.github.modules.github_org>` and {py:mod}`github_repo <saltext.github.modules.github_repo>` modules instead. The `github` execution module remains the namespace for functionality that is not tied to a single organization. The {py:func}`github.list_members_without_mfa <saltext.github.modules.github.list_members_without_mfa>` function and the per-team MFA enforcement of {py:func}`github.team_present <saltext.github.states.github.team_present>` are deprecated without replacement - require 2FA organization-wide in the GitHub settings instead


### Changed

- All API calls are now routed through the PyGithub client, honoring the configured {ghconf}`api_url`, authentication and retry handling uniformly
- Exception tracebacks are only logged at debug loglevel now
- Refactored the GitHub API interaction layer into reusable per-entity modules below {py:mod}`saltext.github.utils.gh`. These raise {py:class}`GitHubApiError <saltext.github.utils.gh.exceptions.GitHubApiError>`/{py:class}`GitHubNotFoundError <saltext.github.utils.gh.exceptions.GitHubNotFoundError>` (subclasses of {py:class}`CommandExecutionError <salt.exceptions.CommandExecutionError>`) instead of returning error indicators. Existing execution module functions behave as before, except that unhandled API errors now surface as the above exceptions instead of raw PyGithub ones.
- The execution module now exclusively relies on public PyGithub APIs instead of internal ones (``_requester``, ``_identity``, ``_rawData``, manual ``PaginatedList`` construction). It also avoids deprecated API paths (``/teams/{team_id}/...``) by addressing teams by slug and checking team memberships via the ``memberships`` endpoints. The minimum supported PyGithub version is now 2.2.


### Added

- Added `default_branch` to {py:func}`github_repo.update <saltext.github.modules.github_repo.update>` and the {py:func}`github_repo.present <saltext.github.states.github_repo.present>` state
- Added `github.query` for making direct calls to arbitrary GitHub API endpoints, transparently following pagination
- Added `github.rate_limit` for querying the API rate limit status of the profile's token
- Added `github.revoke_app_token` for immediately revoking a GitHub App profile's current installation access token (otherwise valid for one hour), e.g. as the last step of an ephemeral CI run
- Added `github_user.list_keys` for listing the verified public SSH keys of any user, defaulting to the token's user, e.g. for use with the `ssh_auth` state module
- Added a persistent cross-process per-connection cache (on by default, opt out via the {ghconf}`cache` profile parameter), serving token/account identities and file-based custom resource grains (validated against each repository's `pushed_at` timestamp) without refetching, e.g. across `salt-call --local` invocations
- Added composite states that generate an SSH keypair in memory via the {py:mod}`ssh_pki <salt.modules.ssh_pki>` module and distribute the public half as a deploy key and the private half as an Actions secret, with optional rotation ({py:func}`github_repo.deploy_key_actions_present <saltext.github.states.github_repo.deploy_key_actions_present>` and the resource-type {py:func}`deploy_key.actions_present <saltext.github.resources.github.states.deploy_key.actions_present>`)
- Added custom repository resource grains sourced from in-repo YAML/JSON files (e.g. copier answers) via the {ghconf}`grains_files <resource:grains_files>` resource declaration key, with per-namespace key filtering, renaming and optional merging into the root grains
- Added management of GitHub Pages sites ({py:func}`github_repo.get_pages <saltext.github.modules.github_repo.get_pages>`/{py:func}`setup_pages <saltext.github.modules.github_repo.setup_pages>`/{py:func}`update_pages <saltext.github.modules.github_repo.update_pages>`/{py:func}`remove_pages <saltext.github.modules.github_repo.remove_pages>` and the {py:func}`github_repo.pages_present <saltext.github.states.github_repo.pages_present>`/{py:func}`pages_absent <saltext.github.states.github_repo.pages_absent>` states)
- Added management of default workflow permissions for the `GITHUB_TOKEN` ({py:func}`github_repo.get_workflow_permissions <saltext.github.modules.github_repo.get_workflow_permissions>`/{py:func}`set_workflow_permissions <saltext.github.modules.github_repo.set_workflow_permissions>` and the {py:func}`github_repo.workflow_permissions_managed <saltext.github.states.github_repo.workflow_permissions_managed>` state)
- Added management of repository Actions secrets, encrypted client-side to the repository public key ({py:func}`github_repo.list_actions_secrets <saltext.github.modules.github_repo.list_actions_secrets>`/{py:func}`get_actions_secret <saltext.github.modules.github_repo.get_actions_secret>`/{py:func}`set_actions_secret <saltext.github.modules.github_repo.set_actions_secret>`/{py:func}`remove_actions_secret <saltext.github.modules.github_repo.remove_actions_secret>` and the {py:func}`github_repo.actions_secret_present <saltext.github.states.github_repo.actions_secret_present>`/{py:func}`actions_secret_absent <saltext.github.states.github_repo.actions_secret_absent>` states)
- Added management of repository deploy keys ({py:func}`github_repo.list_deploy_keys <saltext.github.modules.github_repo.list_deploy_keys>`/{py:func}`get_deploy_key <saltext.github.modules.github_repo.get_deploy_key>`/{py:func}`add_deploy_key <saltext.github.modules.github_repo.add_deploy_key>`/{py:func}`remove_deploy_key <saltext.github.modules.github_repo.remove_deploy_key>` and the {py:func}`github_repo.deploy_key_present <saltext.github.states.github_repo.deploy_key_present>`/{py:func}`deploy_key_absent <saltext.github.states.github_repo.deploy_key_absent>` states)
- Added management of repository environments, including deployment branch policies ({py:func}`github_repo.list_environments <saltext.github.modules.github_repo.list_environments>`/{py:func}`get_environment <saltext.github.modules.github_repo.get_environment>`/{py:func}`set_environment <saltext.github.modules.github_repo.set_environment>`/{py:func}`remove_environment <saltext.github.modules.github_repo.remove_environment>`/{py:func}`list_deployment_branch_policies <saltext.github.modules.github_repo.list_deployment_branch_policies>`/{py:func}`add_deployment_branch_policy <saltext.github.modules.github_repo.add_deployment_branch_policy>`/{py:func}`remove_deployment_branch_policy <saltext.github.modules.github_repo.remove_deployment_branch_policy>` and the {py:func}`github_repo.environment_present <saltext.github.states.github_repo.environment_present>`/{py:func}`environment_absent <saltext.github.states.github_repo.environment_absent>` states)
- Added management of repository labels ({py:func}`github_repo.list_labels <saltext.github.modules.github_repo.list_labels>`/{py:func}`get_label <saltext.github.modules.github_repo.get_label>`/{py:func}`add_label <saltext.github.modules.github_repo.add_label>`/{py:func}`edit_label <saltext.github.modules.github_repo.edit_label>`/{py:func}`remove_label <saltext.github.modules.github_repo.remove_label>` and the {py:func}`github_repo.label_present <saltext.github.states.github_repo.label_present>`/{py:func}`label_absent <saltext.github.states.github_repo.label_absent>` states)
- Added native GitHub App authentication via the {ghconf}`app_id`, {ghconf}`private_key`/{ghconf}`private_key_path` and optional {ghconf}`installation_id` and {ghconf}`permissions` profile parameters. Installation access tokens are minted and refreshed automatically (optionally restricted to a subset of the app's granted permissions), the app's installation on {ghconf}`owner` is discovered when not pinned, and the connection identity derives from the app's identity instead of its short-lived tokens, keeping the persistent {ghconf}`cache` effective across token rotation (e.g. in CI)
- Added scoped {py:mod}`github_org <saltext.github.modules.github_org>` and {py:mod}`github_repo <saltext.github.modules.github_repo>` execution and state modules, which replace the organization- and repository-related functionality of the monolithic `github` modules. Unlike the legacy functions, they raise errors instead of logging them and returning `False`. Collections with a unique natural key (repos, teams, team repos, labels, environments, Actions secrets) are returned as name-keyed mappings, id-addressed ones (issues, PRs, milestones, rulesets, deploy keys) as lists. All collection outputs can be reduced to specific fields via the `fields` argument. The new `github_org.team_present` state manages members as a simple list and drops the legacy per-team MFA enforcement options - require 2FA org-wide in the GitHub organization settings instead
- Added the optional {ghconf}`api_url` profile option for targeting GitHub Enterprise Server instances
- Added the {py:mod}`github <saltext.github.resources.github>` {ref}`Salt resource type <repo-resources>` for Salt 3008.3+, exposing each GitHub repository as an individually targetable resource with per-repository grains and repository-implicit execution and state modules
- Added {py:func}`github.account_info <saltext.github.modules.github.account_info>` for looking up the public profile of any user or organization account, defaulting to the profile's owner
- Added {py:func}`github_org.info <saltext.github.modules.github_org.info>` for looking up the public profile of an organization account, defaulting to the profile's owner and failing on users
- Added {py:func}`github_user.info <saltext.github.modules.github_user.info>` for looking up the public profile of a user account, defaulting to the token's user and failing on organizations
- Extended repository information ({py:func}`github_repo.info <saltext.github.modules.github_repo.info>`/{py:func}`github_repo.list <saltext.github.modules.github_repo.list_>`, but also affects the legacy {py:func}`github.get_repo_info <saltext.github.modules.github.get_repo_info>` and the resource grains) with `visibility`, `archived`, `disabled`, `is_template`, `license`, `topics`, `custom_properties`, `clone_url`, `ssh_url`, `created_at`, `has_discussions`, `has_pages` and `has_projects` (info additionally carries `updated_at`)
- Profile configuration values containing SDB URIs (e.g. `token: sdb://osenv/GITHUB_TOKEN`) are now rendered on access. Salt itself only renders them inside the minion/master configuration during startup, so this makes them work in pillar-sourced profiles as well.
- The new modules support repositories of any owner. Profiles take an {ghconf}`owner` (organization or user; preferred over the legacy `org_name` alias), which defaults to the token's user when unset. Repository listing and creation live on the {py:mod}`github_repo <saltext.github.modules.github_repo>` module ({py:func}`list <saltext.github.modules.github_repo.list_>` / {py:func}`create <saltext.github.modules.github_repo.create>`), and all of its functions and states as well as all functions of the (now strictly organization-scoped) {py:mod}`github_org <saltext.github.modules.github_org>` module accept a per-call `owner` override, so repositories, teams, members and rulesets of foreign organizations can be managed as well. Due to GitHub API limitations, repository creation is only supported for organizations and the authenticated user, private repositories of other users are not listable, tokens without an associated user account (e.g. GitHub App installation tokens) require an explicit `owner` and teams always belong to an organization
- The new {py:mod}`github_org <saltext.github.states.github_org>` and {py:mod}`github_repo <saltext.github.states.github_repo>` states report machine-readable `changes` dictionaries (`created`/`deleted`/`updated` entity names, `old`/`new` setting mappings and `*_added`/`*_removed` name lists) instead of prose


### Fixed

- All states now report the projected changes in test mode, matching the changes reported on actual application.
- Fixed a PyGithub deprecation warning by migrating to `github.Auth.Token` authentication
- Fixed compound states (`github_repo.present`, `github_org.team_present`, environment management) reporting no changes when failing after some changes had already been applied
- Fixed legacy `github` state functions rendering a traceback instead of a failed state when an unexpected `CommandExecutionError` was raised, e.g. caused by missing profile configuration
- Fixed {py:func}`github.add_team <saltext.github.modules.github.add_team>` refreshing the team cache using the default profile instead of the configured one
- Fixed {py:func}`github.get_issues <saltext.github.modules.github.get_issues>`, {py:func}`github.get_issue_comments <saltext.github.modules.github.get_issue_comments>`, {py:func}`github.get_prs <saltext.github.modules.github.get_prs>` and {py:func}`github.get_milestones <saltext.github.modules.github.get_milestones>` crashing with an `AttributeError` when the API returned an error. They now raise a `CommandExecutionError` carrying the API error message.
- Fixed {py:func}`github.get_milestones <saltext.github.modules.github.get_milestones>` / {py:func}`github.get_milestone <saltext.github.modules.github.get_milestone>` crashing on API payloads missing optional keys
- Fixed {py:func}`github.is_team_member <saltext.github.modules.github.is_team_member>` crashing with a `TypeError` when the team does not exist. It now returns `False`.
- Fixed {py:func}`github.remove_repo <saltext.github.modules.github.remove_repo>` raising an exception instead of returning `False` for nonexistent repositories
- Fixed {py:func}`github.repo_present <saltext.github.states.github.repo_present>` not passing the configured profile when creating repositories
- Fixed {py:func}`github.repo_present <saltext.github.states.github.repo_present>` reporting a failed team *removal* when *adding* a repository to a team failed.
- Fixed {py:func}`github.ruleset_absent <saltext.github.states.github.ruleset_absent>` reporting success when the ruleset could not be deleted. The module function returns a truthy error dict on failure, which was mistaken for success, and the failure result was subsequently overwritten by the "does not exist" fallback.
- Fixed {py:func}`github.ruleset_present <saltext.github.states.github.ruleset_present>` drift detection, which compared server-populated fields and iterated the wrong parameter set, and made the ruleset states report forecast changes in test mode
- Fixed {py:func}`github.team_present <saltext.github.states.github.team_present>` crashing when managing team members

## v1.0.0 (2024-08-13)

Initial release of `saltext-github`. This release mostly tracks the functionality in the core Salt code base as of version 3007.1.

### Added

- Add CRUD funtionality for Github rulesets [#11](https://github.com/salt-extensions/saltext-github/issues/11)
