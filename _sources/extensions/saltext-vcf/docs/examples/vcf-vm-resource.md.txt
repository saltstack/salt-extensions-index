# vcf_vm resource

See [Resources Framework](../topics/resources-framework.md).

## Pillar

```yaml
resources:
  vcenter:
    instances:
      mgmt-vc:
        host: mgmt-vc.example.com
        username: administrator@vsphere.local
        password: '{{ pillar["mgmt_vc_password"] }}'
        verify_ssl: false

  vcf_vm:
    instances:
      web-prod-01:
        vcenter: mgmt-vc
        moid: vm-1234
        labels:
          tier: production
          app: web
      web-prod-02:
        vcenter: mgmt-vc
        moid: vm-1235
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

## Targeting

Grains: `tier`, `app` (from `labels:`) + live `name`, `power_state`,
`cpu_count`, `memory_size_MiB`.

```bash
salt -G 'tier:production' vcf_vm.power_state
salt -G 'app:web' vcf_vm.info
salt -G 'app:web' vcf_vm.snapshot_create name=before-deploy memory=false
salt -G 'app:postgres' vcf_vm.reset
salt -G 'tier:production' vcf_vm.power_off
```

## Operations

| Function | Returns |
|---|---|
| `info` | Full VM record |
| `power_state` | `POWERED_ON` / `POWERED_OFF` / `SUSPENDED` |
| `power_on` / `power_off` / `reset` | Action result |
| `snapshot_list` / `snapshot_current` | Snapshot tree |
| `snapshot_create` / `snapshot_revert` / `snapshot_remove` / `snapshot_remove_all` | Lifecycle (SOAP) |
| `tag_assign(tag_id)` / `tag_list_assigned` | vCenter tag association |

## Cross-vCenter fleet

```yaml
resources:
  vcenter:
    instances:
      mgmt-vc:    {host: mgmt-vc.example.com, ...}
      prod-vc-1:  {host: prod-vc-1.example.com, ...}
      prod-vc-2:  {host: prod-vc-2.example.com, ...}

  vcf_vm:
    instances:
      shared-tools-vm:
        vcenter: mgmt-vc
        moid: vm-50
        labels: {tier: shared}
      west-web-01:
        vcenter: prod-vc-1
        moid: vm-1000
        labels: {tier: production, region: west}
      east-web-01:
        vcenter: prod-vc-2
        moid: vm-2000
        labels: {tier: production, region: east}
```

```bash
salt -G 'region:west' vcf_vm.power_off
```
