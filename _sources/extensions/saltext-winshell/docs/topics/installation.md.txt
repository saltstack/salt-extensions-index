# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Winshell extension:
  pip.installed:
    - name: winshell
```
:::

:::{tab} Onedir installation
```bash
salt-pip install winshell
```
:::

:::{tab} Regular installation
```bash
pip install winshell
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
