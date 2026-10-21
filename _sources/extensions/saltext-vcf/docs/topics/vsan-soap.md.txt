# vSAN

vCenter REST has no vSAN surface in VCF 9.x. `saltext-vcf` uses the
legacy SOAP/VMODL service at `/vsanHealth` with a `SoapStubAdapter`
that reuses the vCenter session cookie (no separate auth).

## Modules

| Module | Surface |
|---|---|
| `vcf_vsan_cluster` | Cluster-level reconfigure (dedup/compression, encryption, ESA vs OSA, fault tolerance) |
| `vcf_vsan_disk` | Disk group + disk membership |
| `vcf_vsan_fault_domain` | Fault domain definition + host assignment |
| `vcf_vsan_health` | Health summary, silent health checks |

## Configuration

vSAN piggybacks on the `vcenter` pillar block; no separate `vsan:`
section.

```yaml
saltext.vcf:
  vcenter:
    host: mgmt-vc.example.com
    username: administrator@vsphere.local
    password: secret
    verify_ssl: false
```

## Examples

```bash
salt-call vcf_vsan_health.query_cluster_health cluster=domain-c9
salt-call vcf_vsan_health.list_silent_checks cluster=domain-c9
salt-call vcf_vsan_disk.list_disk_groups cluster=domain-c9
salt-call vcf_vsan_fault_domain.list_ cluster=domain-c9
```

## ESA

VCF 9.x defaults to vSAN ESA. Read paths handle ESA transparently.
`vcf_vsan_cluster.reconfigure` requires ESA-compatible spec inputs;
see the VMware ESA documentation.

## Auth

- vCenter REST acquires the session via `POST /api/session`.
- The vSAN SOAP stub is `SoapStubAdapter(path="/vsanHealth", ...)`;
  the vCenter session cookie is attached.
- Token cache keyed by `(host, username)`. Call
  `saltext.vcf.utils.vsan.invalidate_session(opts)` to refresh.

## Known issues

- vSAN method names vary across VCF versions. VCF 9.x uses
  `QueryClusterHealthSummary` and `GetVsanClusterSilentChecks`. The
  client catches both `vmodl.MethodFault` and `vim.fault.VimFault` to
  surface a clear error on older builds.
- `vsanHostConfig` is `None` on VCF 9.2 hosts; the fault-domain client
  iterates `cluster.host` directly.
- SDDC Manager returns 500 (not 404) for unknown vSAN UUIDs.
