# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Stalekey extension:
  pip.installed:
    - name: saltext-stalekey
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-stalekey
```
:::

:::{tab} Regular installation
```bash
pip install saltext-stalekey
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
