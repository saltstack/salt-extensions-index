# Salt Resources Framework

Each minion can publish multiple addressable instances of a managed
component as Salt resources. Operators then target subsets by grain.

The Resources framework requires `salt.utils.resources`. On builds
without it, the `saltext.vcf.resources` subpackage is dormant
(`__virtual__` returns `False`); use the flat-pillar config from
[Configuration](configuration.md) instead.

## Types

| Type | One resource per | Pillar key |
|---|---|---|
| `vcenter` | vCenter Server | `resources.vcenter.instances` |
| `sddc` | SDDC Manager | `resources.sddc.instances` |
| `nsx` | NSX Manager | `resources.nsx.instances` |
| `vcfops` | VCF Operations appliance | `resources.vcf_ops.instances` |
| `esxi` | Standalone ESXi host | `resources.esxi.instances` |
| `vcf_vm` | Virtual machine (references a `vcenter` id) | `resources.vcf_vm.instances` |

## Pillar

```yaml
resources:
  vcenter:
    instances:
      mgmt-vc:
        host: mgmt-vc.example.com
        username: administrator@vsphere.local
        password: secret
        verify_ssl: false
      prod-vc:
        host: prod-vc.example.com
        username: administrator@vsphere.local
        password: other-secret
        verify_ssl: false
  sddc:
    instances:
      sddc-mgmt:
        host: sddc-manager.example.com
        username: administrator@vsphere.local
        password: secret
        verify_ssl: false
  nsx:
    instances:
      mgmt-nsx:
        host: mgmt-nsx.example.com
        username: admin
        password: secret
        verify_ssl: false
  vcf_ops:
    instances:
      ops-prod:
        host: ops.example.com
        username: admin
        password: secret
        auth_source: LOCAL
        verify_ssl: false
```

## Targeting

Each resource publishes `resource_type`, `resource_id`, and `host` as
grains, plus type-specific live fields (e.g. `name`, `power_state` for
`vcf_vm`).

```bash
# Minions managing vCenter resource 'mgmt-vc'
salt -C 'T@vcenter:mgmt-vc' vcf_vcenter_cluster.list_

# VMs labeled tier=production
salt -G 'tier:production' vcf_vm.power_off

# VMs labeled app=web (across every minion's vCenters)
salt -G 'app:web' vcf_vm.snapshot_create name=before-deploy
```

## `vcf_vm` resource

Each entry references a `vcenter` instance by id; one minion can
manage VMs across multiple vCenters.

```yaml
resources:
  vcenter:
    instances:
      mgmt-vc:
        host: mgmt-vc.example.com
        username: administrator@vsphere.local
        password: secret
  vcf_vm:
    instances:
      web-prod-01:
        vcenter: mgmt-vc
        moid: vm-1234
        labels:
          tier: production
          app: web
      db-prod-01:
        vcenter: mgmt-vc
        moid: vm-1289
        labels:
          tier: production
          app: postgres
```

`labels:` entries become top-level grains. Live grains pulled from
vCenter at `grains()`: `name`, `power_state`, `cpu_count`,
`memory_size_MiB`.

Per-resource operations:

| Function | Notes |
|---|---|
| `info` | Full VM record |
| `power_state` | Current power state string |
| `power_on` / `power_off` / `reset` | Power control |
| `snapshot_list` / `snapshot_current` | Snapshot tree |
| `snapshot_create` / `snapshot_revert` / `snapshot_remove` / `snapshot_remove_all` | Lifecycle (SOAP) |
| `tag_assign` / `tag_list_assigned` | vCenter tag association |

VM auto-discovery from vCenter (phase 10b) is deferred pending
`discover()` pagination in the Resources framework.

## VKS handoff

The Supervisor cluster's Kubernetes API is consumed via
`saltext-kubernetes`. After
`vcf_vks.fetch_kubeconfig(<cluster_id>)`:

```yaml
resources:
  kubernetes:
    instances:
      supervisor-prod:
        kubeconfig: /home/salt/.kube/vks-cluster-domain-c9.config
```

See [VKS Bridge](vks-bridge.md).
