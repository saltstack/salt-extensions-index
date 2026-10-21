# VKS examples

See [VKS Bridge](../topics/vks-bridge.md).

## Pre-enablement probes

```bash
salt-call vcf_vcenter_supervisor.list_compatibility
salt-call vcf_vcenter_supervisor_compat.get_cluster_size_info
salt-call vcf_vcenter_supervisor_compat.list_dvs_compatibility cluster=domain-c9
salt-call vcf_vcenter_supervisor_compat.list_edge_cluster_compatibility \
    cluster=domain-c9 distributed_switch=<dvs-id>
```

## Enable / disable

```bash
salt-call vcf_vcenter_supervisor.enable_cluster \
    cluster_id=domain-c9 \
    enable_spec='{"size_hint":"TINY","ephemeral_storage_policy":"...", ...}'

salt-call vcf_vcenter_supervisor.disable_cluster cluster_id=domain-c9
```

## Supervisor Services

```bash
salt-call vcf_vcenter_supervisor_service.list_
salt-call vcf_vcenter_supervisor_service.get tkg.vsphere.vmware.com
salt-call vcf_vcenter_supervisor_service.list_versions tkg.vsphere.vmware.com

salt-call vcf_vcenter_supervisor_service.create \
    service_spec='{"supervisor_service":"my-svc","content_type":"YAML","content":"<base64>","trusted":true}'

salt-call vcf_vcenter_supervisor_service.activate   tkg.vsphere.vmware.com
salt-call vcf_vcenter_supervisor_service.deactivate tkg.vsphere.vmware.com
```

```yaml
TKG activated:
  vcf_vcenter_supervisor_service.activated:
    - name: tkg.vsphere.vmware.com
```

## VM classes

```bash
salt-call vcf_vcenter_vm_class.list_
salt-call vcf_vcenter_vm_class.get guaranteed-small
```

```yaml
Custom VM class:
  vcf_vcenter_vm_class.present:
    - name: gpu-medium
    - cpu_count: 8
    - memory_MB: 32768
    - description: 8 vCPU / 32 GiB / 1x GPU
```

## Namespaces

```bash
salt-call vcf_vcenter_supervisor.list_namespaces
salt-call vcf_vcenter_supervisor.create_namespace \
    namespace_spec='{"cluster":"domain-c9","namespace":"team-a"}'
salt-call vcf_vcenter_supervisor.delete_namespace team-a
```

## Software lifecycle

```bash
salt-call vcf_vcenter_supervisor_software.list_
salt-call vcf_vcenter_supervisor_software.get domain-c9

salt-call vcf_vcenter_supervisor_software.upgrade domain-c9 \
    upgrade_spec='{"desired_version":"v1.28.2+vmware.1","ignore_precheck_warnings":false}'
```

## Kubeconfig fetch

```bash
salt-call vcf_vks.fetch_kubeconfig cluster_id=domain-c9
salt-call vcf_vks.fetch_kubeconfig cluster_id=domain-c9 namespace=team-a
salt-call vcf_vks.saltext_kubernetes_available
```

Files land at `~/.kube/vks-<cluster>.config` with mode `0o600`. Wire a
`kubernetes` resource pointing at the kubeconfig path — see
[VKS Bridge](../topics/vks-bridge.md).
