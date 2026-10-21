# Installation

`saltext-nebula` is a Salt extension for managing [Nebula](https://github.com/slackhq/nebula) mesh VPN deployments. It provides centralized certificate authority management, automated certificate distribution, cross-platform configuration generation, and certificate lifecycle monitoring.

## Requirements

- Salt 3007 or later
- Python 3.10 or later
- `nebula-cert` binary on the Salt master (for certificate generation)

## Installing the Extension

Generally, Salt extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Nebula extension:
  pip.installed:
    - name: saltext-nebula
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-nebula
```
:::

:::{tab} Regular installation
```bash
pip install saltext-nebula
```
:::

:::{hint}
Salt extensions are not distributed automatically via the fileserver like custom modules. They need to be installed on each node where you want them available:
- Install on the **Salt master** for runner functionality (CA management, certificate generation)
- Install on **minions** for execution modules, states, and beacons
:::

## Alternative: GitFS Distribution

For development workflows or environments where pip installation is not practical, you can distribute the extension components via GitFS. This pulls each component directly into the Salt fileserver.

Add the following to `/etc/salt/master` or `/etc/salt/master.d/gitfs.conf`:

```yaml
fileserver_backend:
  - git
  - roots

gitfs_remotes:
  - https://github.com/salt-extensions/saltext-nebula.git:
    - name: saltext-nebula-modules
    - root: src/saltext/nebula/modules
    - mountpoint: salt://_modules
    - base: main
    - ref_types:
      - branch
  - https://github.com/salt-extensions/saltext-nebula.git:
    - name: saltext-nebula-states
    - root: src/saltext/nebula/states
    - mountpoint: salt://_states
    - base: main
    - ref_types:
      - branch
  - https://github.com/salt-extensions/saltext-nebula.git:
    - name: saltext-nebula-runners
    - root: src/saltext/nebula/runners
    - mountpoint: salt://_runners
    - base: main
    - ref_types:
      - branch
  - https://github.com/salt-extensions/saltext-nebula.git:
    - name: saltext-nebula-beacons
    - root: src/saltext/nebula/beacons
    - mountpoint: salt://_beacons
    - base: main
    - ref_types:
      - branch

gitfs_refspecs:
  - '+refs/heads/main:refs/remotes/origin/main'
  - '+refs/heads/*:refs/remotes/origin/*'
  - '+refs/tags/*:refs/tags/*'
```

After configuring GitFS, refresh the fileserver and sync modules to minions:

```bash
# Restart the salt master
systemctl restart salt-master

# Clear and refresh the gitfs cache
salt-run fileserver.clear_cache backend=gitfs
salt-run fileserver.update backend=gitfs

# Sync modules to target minions
salt '*' saltutil.sync_all
```

## Verifying Installation

After installation, verify the extension is loaded:

```bash
# On the master - check runner availability
salt-run nebula.list_certificates

# On a minion - check execution module
salt '*' nebula.detect_paths
```
