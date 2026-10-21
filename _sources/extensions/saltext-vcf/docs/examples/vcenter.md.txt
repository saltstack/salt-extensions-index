# vCenter examples

## Inventory

```bash
salt-call vcf_vcenter_cluster.list_
salt-call vcf_vcenter_host.list_
salt-call vcf_vcenter_vm.list_
salt-call vcf_vcenter_datacenter.list_
salt-call vcf_vcenter_datastore.list_
salt-call vcf_vcenter_network.list_
salt-call vcf_vcenter_storage_policy.list_
```

## VM lifecycle (REST)

```bash
salt-call vcf_vcenter_vm.get vm-100
salt-call vcf_vcenter_vm.power_on vm-100
salt-call vcf_vcenter_vm.power_off vm-100
salt-call vcf_vcenter_vm.reset vm-100
```

## VM snapshots (SOAP)

REST has no snapshot surface in VCF 9.x; snapshots route through pyVmomi.

```bash
salt-call vcf_vim_vm_snapshot.list_ vm-100
salt-call vcf_vim_vm_snapshot.current vm-100

salt-call vcf_vim_vm_snapshot.create vm-100 baseline \
    description="pre-upgrade" memory=true quiesce=true

salt-call vcf_vim_vm_snapshot.revert vm-100 baseline
salt-call vcf_vim_vm_snapshot.remove vm-100 baseline
salt-call vcf_vim_vm_snapshot.remove_all vm-100
```

## Tagging

```bash
salt-call vcf_vcenter_tag.list_
salt-call vcf_vcenter_tag.create production category-1 description="Prod fleet"
salt-call vcf_vcenter_tag.assign urn:vmomi:Tag:prod VirtualMachine vm-100
salt-call vcf_vcenter_tag.list_assigned VirtualMachine vm-100
```

## Cluster Configuration Profile (vSphere 9)

Desired-state profile API. Replaces direct ESXi REST when hosts are
vCenter-managed.

```bash
salt-call vcf_cluster_config.get_profile domain-c9
salt-call vcf_cluster_config.draft_create domain-c9 spec='{...}'
salt-call vcf_cluster_config.draft_preview domain-c9 draft_id=...
salt-call vcf_cluster_config.draft_apply  domain-c9 draft_id=...
salt-call vcf_cluster_config.check_compliance domain-c9
```

## Appliance

```bash
salt-call vcf_vcenter_appliance.version
salt-call vcf_vcenter_appliance.health_system
salt-call vcf_vcenter_appliance.services_list
salt-call vcf_vcenter_appliance.dns_get
salt-call vcf_vcenter_appliance.logging_forwarding_get
```

## KMS providers

```bash
salt-call vcf_vcenter_kms.list_
salt-call vcf_vcenter_kms.get my-kms
salt-call vcf_vcenter_kms.create '{"provider":"my-kms","type":"NATIVE", ...}'
```
