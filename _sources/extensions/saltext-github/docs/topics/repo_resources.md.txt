(repo-resources)=

# Managing repositories as resources

:::{versionadded} 1.1.0
:::

On Salt 3008.3 and later, this extension provides the `github`
[resource type](https://docs.saltproject.io/en/latest/topics/resources/index.html),
which exposes each GitHub repository as an individually targetable
Salt resource. Compared to the classic
{py:mod}`github_repo <saltext.github.modules.github_repo>` modules,
resources offer:

- direct targeting of repositories (`salt 'my-org/my-repo'` /
  `salt -C 'T@github:my-org/my-repo'`), including grain-based
  targeting across all managed repositories
  (`salt -G 'default_branch:master'`)
- per-repository grains (owner, default branch, visibility, ...) - a
  repository resource's grains can optionally even include data files
  from the repo itself
- repository-implicit execution and state modules – SLS files describe
  one repository's desired configuration and are applied per resource,
  without threading `repo_name`/`owner` through every call

The classic modules remain fully supported (and are the only option on
Salt 3006/3007); both are thin layers over the same core
implementation.

:::{note}
While the resource subsystem was introduced in Salt 3008.0, this
extension requires **3008.3+**: that release made the per-resource
execution loader deny-by-default, so that jobs dispatched to a
resource only see the modules this extension ships for it. On earlier
3008 releases, the loader was additive – stock and classic extension
modules leaked into the resource context – which this extension's
modules are neither written nor tested for.
:::

## Setup

Declare the resource type in the managing minion's pillar, under the
subtree selected by the {conf_minion}`resource_pillar_key` minion
option (default: `resources`):

```{code-block} yaml
:caption: e.g. `/etc/salt/minion.d/github_resource.yml`

resources:
  github:
    profile: github
    owners:
      - my-org
```

All declaration keys – repository include/exclude patterns, archived
handling and the profile, each overridable per owner (e.g. for
repositories spanning credentials) – are described in the
{ref}`configuration guide <github-resource-configuration>`. The
referenced profiles are configured as usual (see the
{ref}`profile parameters <profile>`).

After changing the declaration, refresh the minion's resources:

```bash
salt 'minion' saltutil.refresh_resources
```

Each repository is registered as a resource named `<owner>/<repo>`,
i.e. with the SRN `github:<owner>/<repo>`.

## Targeting

```bash
# One repository, by ID
salt 'my-org/my-repo' test.ping

# One repository, by SRN
salt -C 'T@github:my-org/my-repo' test.ping

# By resource grain
salt -G 'default_branch:master' repo.info
```

The resource grains carry the repository's identity and basic
metadata: `id`, `owner`, `repo`, `full_name`, `private`, `visibility`,
`fork`, `archived`, `disabled`, `is_template`, `default_branch`,
`language`, `license`, `topics`, `custom_properties`, `html_url`,
`clone_url`, `ssh_url`, `description`, `homepage`, `created_at`,
`has_discussions`, `has_pages` and `has_projects`.

Custom grains sourced from files inside each repository can be
declared via {ghconf}`resource:grains_files`, each namespace becoming
a grain key next to the builtin ones (the special `_` namespace merges
into the root grains, never overwriting existing keys):

```bash
salt -G 'copier:template_version:2*' repo.info
```

:::{important}
Custom grains are controlled by anyone who can commit to the
respective repository. Restrict the exposed keys via `include`
allowlists and keep that trust model in mind when building targeting
expressions.
:::

:::{hint}
File-based grains and account metadata survive across processes (e.g.
`salt-call --local` invocations) in a persistent cache, which is
enabled by default (opt out per profile via {ghconf}`cache`). Cached
file contents stay valid until the respective repository receives a
new push.
:::

## Execution modules

Jobs dispatched to a `github` resource use repository-implicit,
entity-scoped execution modules instead of the classic ones:

```bash
salt 'my-org/my-repo' repo.update description='Managed by Salt'
salt 'my-org/my-repo' actions.set_secret MY_SECRET hunter2
salt 'my-org/my-repo' deploy_key.list
salt 'my-org/my-repo' environment.get release
```

See the
{doc}`module reference </ref/resources/saltext.github.resources.github>`
for the complete list.

## States

State runs dispatched to a resource converge that repository. A
typical `repo_setup.sls`:

```yaml
Repository settings are managed:
  repo.managed:
    - description: Managed by Salt
    - has_issues: true
    - teams:
        my-team: push

release:
  environment.present:
    - deployment_branches:
        - main
  label.present:
    - color: '#00FF00'

Autorelease deploy key is present:
  deploy_key.present:
    - name: autorelease
    - key: ssh-ed25519 AAAA...

Workflow permissions are restricted:
  actions.workflow_permissions_managed:
    - default_workflow_permissions: read
    - can_approve_pull_request_reviews: true
```

```bash
salt 'my-org/my-repo' state.apply repo_setup
```

Unlike the classic
{py:func}`github_repo.present <saltext.github.states.github_repo.present>`
state,
{py:func}`repo.present <saltext.github.resources.github.states.repo.managed>`
never creates the repository – a resource's existence is a given.
Repository creation (and deletion) remains a classic-module task on
the managing minion:

```bash
salt 'minion' github_repo.create my-new-repo
salt 'minion' saltutil.refresh_resources
```
