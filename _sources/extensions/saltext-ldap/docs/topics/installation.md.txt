# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Ldap extension:
  pip.installed:
    - name: saltext-ldap
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-ldap
```
:::

:::{tab} Regular installation
```bash
pip install saltext-ldap
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
