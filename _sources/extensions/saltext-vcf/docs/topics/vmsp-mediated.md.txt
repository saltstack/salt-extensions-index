# VMSP

VMSP is the embedded k3s cluster hosting VCF platform microservices
(Common Services, Domain Manager, Operations Manager, LCM, SDDC
Manager UI). The three ingresses (`vsp-platform`, `vsp-fleet`,
`vsp-instance`) are internal-only; external callers consume VMSP
through SDDC Manager's `/v1/vcf-services`.

## Module

| Module | Purpose |
|---|---|
| `vcf_vcf_services` | List/get the VMSP service catalog mediated by SDDC Manager |

No separate `vmsp:` pillar block; uses the existing `sddc_manager`
connection.

## Catalog

VCF 9.2 exposes at least:

| Name | Backing ingress |
|---|---|
| `COMMON_SERVICES` | `vsp-platform` |
| `DOMAIN_MANAGER` | `vsp-platform` |
| `OPERATIONS_MANAGER` | `vsp-fleet` |
| `LCM` | `vsp-fleet` / `vsp-instance` |
| `SDDC_MANAGER_UI` | `vsp-platform` |

Each entry: `id`, `name`, `version`, `status` (`UP`, `DOWN`,
`DEGRADED`).

## Examples

```bash
salt-call vcf_vcf_services.list_
salt-call vcf_vcf_services.get <uuid>
salt-call vcf_vcf_services.get_by_name COMMON_SERVICES
salt-call vcf_vcf_services.status_map
salt-call vcf_vcf_services.healthy
```

## State (read-only)

```yaml
Assert COMMON_SERVICES UP:
  vcf_vcf_services.healthy:
    - name: COMMON_SERVICES
```

Never modifies VMSP. Use as a precondition for SDDC LCM operations.

## Why mediated only

The VMSP ingresses require an internal JWT issued by VIDB, not the
SDDC Manager bearer token. Direct k3s API access is out of scope —
SDDC Manager is the supported integration boundary, and going around
it couples the extension to internals that change across VCF
releases.

## Resources framework

The operations are also exposed on the `sddc` resource type:

```bash
salt -C 'T@sddc:sddc-prod' sddc.vcf_services_list
```

See [Resources Framework](resources-framework.md).
