# saltext.vcf

Salt extension for VMware Cloud Foundation 9.x. Targets the full VCF
stack: vCenter, NSX, SDDC Manager, VCF Operations, VKS (Supervisor),
VMSP (mediated), vSAN, and standalone ESXi.

## Coverage

- **vCenter** — REST `/api/` for clusters, hosts, VMs, datacenters,
  datastores, networks, storage policies, content libraries, folders,
  resource pools, tags, custom attributes, appliance services, KMS
  providers; pyVmomi/SOAP for alarms, perf, extensions, VM snapshots.
- **vSphere 9 Cluster Configuration Profile** — desired-state profile
  API for vCenter-managed clusters (replaces direct ESXi REST).
- **NSX** — Policy API (segments, tier-0/tier-1, groups, security
  policies, firewall rules, services, context profiles, NAT, IP
  blocks/pools, DHCP, edge clusters) and Management API (node,
  cluster status, transport zones/nodes, compute collections, RBAC).
- **SDDC Manager** — hosts, clusters, workload domains, vCenters,
  bundles, network pools, releases, upgrades, certificates,
  credentials, VMSP service health via `/v1/vcf-services`.
- **VCF Operations** — resources, adapters, alert/symptom definitions,
  active alerts, policies, notifications, recommendations, RBAC
  (sources/roles/users/groups/privileges), collectors, credentials,
  super metrics, resource groups, reports, maintenance schedules,
  tasks, solutions, node status.
- **VKS** — Supervisor enablement, services catalog, namespaces, VM
  classes, software lifecycle, compatibility probes, kubeconfig fetch
  bridge to [saltext-kubernetes].
- **vSAN** — cluster config, disk groups, fault domains, health (SOAP
  at `/vsanHealth`).
- **Salt Resources framework** — `vcenter`, `sddc`, `nsx`, `vcfops`,
  `esxi`, `vcf_vm` resource types for fleet-style management with
  grain-based targeting.

~80 execution modules, 27 state modules, 82 REST/SOAP clients across
six VCF components.

## Quickstart

```bash
pip install saltext-vcf
```

Configure pillar:

```yaml
saltext.vcf:
  vcenter:
    host: mgmt-vc.example.com
    username: administrator@vsphere.local
    password: secret
    verify_ssl: false
  sddc_manager:
    host: sddc-manager.example.com
    username: administrator@vsphere.local
    password: secret
    verify_ssl: false
  nsx:
    host: mgmt-nsx.example.com
    username: admin
    password: secret
    verify_ssl: false
  vcf_ops:
    host: ops.example.com
    username: admin
    password: secret
    verify_ssl: false
```

Run from any minion with the extension installed:

```bash
salt-call vcf_vcenter_cluster.list_
salt-call vcf_sddc_domain.list_
salt-call vcf_nsx_segment.list_
salt-call vcf_vcfops_deployment.healthy
salt-call vcf_vcf_services.status_map
```

## Extras

| Extra | Adds |
|---|---|
| `[vcenter]` | `vmware-vcenter` SDK for advanced vCenter REST flows |
| `[sddc]` | `vmware-vcf` SDK for SDDC Manager flows |
| `[vks]` | `saltext-kubernetes` + `kubernetes` for the VKS kubeconfig bridge |

```bash
pip install 'saltext-vcf[vks]'
```

## Documentation

Full docs at <https://salt-extensions.github.io/saltext-vcf/>.

Local build:

```bash
pip install -e '.[docs]'
make -C docs html
xdg-open docs/_build/html/index.html
```

Topic guides under `docs/topics/`:
- [Installation](docs/topics/installation.md)
- [Configuration](docs/topics/configuration.md)
- [Resources Framework](docs/topics/resources-framework.md)
- [VKS / Supervisor bridge](docs/topics/vks-bridge.md)
- [vSAN over SOAP](docs/topics/vsan-soap.md)
- [VMSP mediated access](docs/topics/vmsp-mediated.md)

Examples per component live under `docs/examples/`.

## Development

```bash
pip install -e '.[dev,tests,lint]'
pre-commit install
pytest tests/ -q
```

Live integration tests run against a real VCF lab and live in a separate
integration repository; they're not part of the unit test suite here.

## License

Apache 2.0. See [LICENSE](LICENSE).

[saltext-kubernetes]: https://github.com/salt-extensions/saltext-kubernetes
