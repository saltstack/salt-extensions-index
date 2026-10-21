# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Acme extension:
  pip.installed:
    - name: saltext-acme
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-acme
```
:::

:::{tab} Regular installation
```bash
pip install saltext-acme
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
