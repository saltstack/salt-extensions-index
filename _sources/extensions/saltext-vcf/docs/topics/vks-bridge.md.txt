# VKS / Supervisor

VKS overlays a Kubernetes control plane on a vSphere cluster.
`saltext-vcf` handles the vCenter-side: Supervisor enablement,
namespaces, VM classes, service catalog. Kubernetes-side workload
operations are delegated to [`saltext-kubernetes`].

## vCenter-side modules

| Module | Surface |
|---|---|
| `vcf_vcenter_supervisor` | Enable/disable Supervisor, namespaces, compatibility listing |
| `vcf_vcenter_supervisor_service` | Service catalog (TKG, Velero, Harbor, …) + activate/deactivate |
| `vcf_vcenter_supervisor_software` | K8s version state + upgrade trigger |
| `vcf_vcenter_supervisor_compat` | Pre-enable DVS / edge / sizing probes |
| `vcf_vcenter_vm_class` | VM class catalog |
| `vcf_vks` | Materialize a Supervisor kubeconfig to disk |

## Kubernetes-side

[`saltext-kubernetes`] covers everything inside the Supervisor: Pods,
Deployments, StatefulSets, DaemonSets, ConfigMaps, Secrets, Services,
Ingresses, PV/PVC, plus TKG workload-cluster CRDs.

## Flow

### 1. Probe

```bash
salt-call vcf_vcenter_supervisor.list_compatibility
salt-call vcf_vcenter_supervisor_compat.get_cluster_size_info
salt-call vcf_vcenter_supervisor_compat.list_dvs_compatibility cluster=domain-c9
```

### 2. Enable

```bash
salt-call vcf_vcenter_supervisor.enable_cluster \
    cluster_id=domain-c9 \
    enable_spec='{"size_hint":"TINY", ...}'
```

### 3. Register services

```bash
salt-call vcf_vcenter_supervisor_service.list_
salt-call vcf_vcenter_supervisor_service.create \
    service_spec='{"supervisor_service":"my-svc","content_type":"YAML","content":"<base64>","trusted":true}'
salt-call vcf_vcenter_supervisor_service.activate my-svc
```

### 4. Create namespaces

```bash
salt-call vcf_vcenter_supervisor.create_namespace \
    namespace_spec='{"cluster":"domain-c9","namespace":"team-a"}'
```

### 5. Fetch kubeconfig

```bash
salt-call vcf_vks.fetch_kubeconfig cluster_id=domain-c9
# → {"path": "/home/salt/.kube/vks-domain-c9.config", "kubeconfig": "<yaml>"}

# Namespace-scoped:
salt-call vcf_vks.fetch_kubeconfig cluster_id=domain-c9 namespace=team-a
```

Files are written with mode `0o600`.

### 6. Delegate to saltext-kubernetes

```yaml
resources:
  kubernetes:
    instances:
      supervisor-domain-c9:
        kubeconfig: /home/salt/.kube/vks-domain-c9.config
```

```bash
salt-call kubernetes.pod_list namespace=team-a
salt-call kubernetes.deployment_create_or_replace ...
```

## Bridge probe

```bash
salt-call vcf_vks.saltext_kubernetes_available
```

Returns `True` only when both `saltext.kubernetes` and `kubernetes`
(the Python client) are importable.

```bash
pip install 'saltext-vcf[vks]'
```

## Gotchas

- Older vSphere builds lack the per-cluster kubeconfig endpoint
  (`/api/vcenter/namespace-management/clusters/{id}/kubeconfig`). The
  module falls back to the user-scoped path automatically.
- The Supervisor's K8s API is on the LB-fronted address (typically Avi
  in VCF 9.x). Confirm the `server:` URL in the kubeconfig is routable
  from the minion before delegating.
- Supervisor tokens have finite lifetime. Schedule periodic
  `vcf_vks.fetch_kubeconfig` for long-lived bridges.

[`saltext-kubernetes`]: https://github.com/salt-extensions/saltext-kubernetes
