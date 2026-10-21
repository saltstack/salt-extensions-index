# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Github extension:
  pip.installed:
    - name: saltext-github
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-github
```
:::

:::{tab} Regular installation
```bash
pip install saltext-github
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
