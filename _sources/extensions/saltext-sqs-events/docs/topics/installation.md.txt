# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Sqs-events extension:
  pip.installed:
    - name: saltext-sqs-events
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-sqs-events
```
:::

:::{tab} Regular installation
```bash
pip install saltext-sqs-events
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
