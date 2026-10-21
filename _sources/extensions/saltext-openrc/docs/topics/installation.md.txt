# Installation

The extension must be installed into the same Python environment Salt uses on
each minion you want OpenRC service support on. Saltexts are not distributed
automatically via the fileserver like custom modules.

:::{tab} State
```yaml
Install saltext-openrc:
  pip.installed:
    - name: saltext-openrc
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-openrc
```
:::

:::{tab} Regular installation
```bash
pip install saltext-openrc
```
:::

:::{hint}
On many OpenRC-based distributions Salt uses the system Python, so a regular
``pip install`` is correct for most setups. If you have installed Salt into a
virtual environment, activate it first.
:::

## Verifying the installation

After installing, confirm that Salt has loaded the module on your minion:

```bash
salt <minion-id> sys.doc service.start
```

This should return documentation pulled from this extension. If it returns
nothing or shows a different provider, see :ref:`module-provider-override` in
the Salt documentation.
