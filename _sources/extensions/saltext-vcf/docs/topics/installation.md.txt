# Installation

Install into the same Python environment Salt uses.

:::{tab} salt-pip (Onedir)
```bash
salt-pip install saltext-vcf
```
:::

:::{tab} pip
```bash
pip install saltext-vcf
```
:::

:::{tab} Salt state
```yaml
Install saltext-vcf:
  pip.installed:
    - name: saltext-vcf
```
:::

Saltexts are not distributed via the fileserver. Install on every node
that needs the modules.

## Extras

Base install pulls `pyvmomi` (SOAP/VMODL) and `pywbem` (CIM/WBEM).

| Extra | Adds |
|---|---|
| `[vcenter]` | `vmware-vcenter` SDK |
| `[sddc]` | `vmware-vcf` SDK |
| `[vks]` | `saltext-kubernetes` + `kubernetes` for the VKS kubeconfig bridge |

```bash
pip install 'saltext-vcf[vks]'
```

## Verify

```bash
salt-call --local sys.list_modules | grep vcf_
salt-call --local sys.list_states  | grep vcf_
```

Expect ~80 modules and ~27 states. If empty, the install landed in a
different Python than Salt's:

```bash
salt-call --local config.get pip_target
salt-call --local sys.doc vcf_vcenter_cluster
```

## Salt version

Targets Salt 3006+. The `saltext.vcf.resources` subpackage requires
`salt.utils.resources`; on builds without it, `__virtual__` returns
`False` and the resources framework integration is unavailable. The
flat-pillar path still works.

## Next

* [Configuration](configuration.md)
* [Reference](../ref/modules/index.rst)
