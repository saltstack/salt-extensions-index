# Installation

The extension must be installed into the same Python environment Salt uses on
each minion you want Alpine support on. Saltexts are not distributed
automatically via the fileserver like custom modules.

:::{tab} State
```yaml
Install saltext-alpine:
  pip.installed:
    - name: saltext-alpine
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-alpine
```
:::

:::{tab} Regular installation
```bash
pip install saltext-alpine
```
:::

:::{hint}
On Alpine, Salt is typically installed from the community repository. The
Python environment Salt uses is the system Python, so a regular ``pip install``
is correct for most setups. If you have installed Salt into a virtual
environment, activate it first.
:::

## Verifying the installation

After installing, confirm that Salt has loaded the modules on your Alpine
minion:

```bash
salt <minion-id> sys.doc pkg.install
salt <minion-id> sys.doc service.start
```

Both commands should return documentation pulled from this extension. If they
return nothing or show a different provider, see
:ref:`module-provider-override` in the Salt documentation.
