# SDDC Manager examples

## Inventory

```bash
salt-call vcf_sddc_host.list_
salt-call vcf_sddc_cluster.list_
salt-call vcf_sddc_domain.list_
salt-call vcf_sddc_vcenters.list_
salt-call vcf_sddc_network_pools.list_
```

## Lifecycle

```bash
salt-call vcf_sddc_bundles.list_
salt-call vcf_sddc_releases.list_
salt-call vcf_sddc_upgrades.list_
salt-call vcf_sddc_certificates.list_ <domain-id>
salt-call vcf_sddc_certificates.list_csrs <domain-id>
```

## Credentials

```bash
salt-call vcf_sddc_credentials.list_

salt-call vcf_sddc_credentials.rotate \
    elements='[{"resourceName":"esxi01","resourceType":"ESXI","credentialType":"SSH"}]'
```

## Host commissioning

```yaml
Commission ESXi:
  vcf_sddc_host.present:
    - name: esxi-new-01
    - specs:
        - fqdn: esxi-new-01.example.com
          username: root
          password: secret
          networkPoolName: pool-1
          storageType: VSAN
```

## VMSP service health (mediated)

```bash
salt-call vcf_vcf_services.list_
salt-call vcf_vcf_services.get_by_name COMMON_SERVICES
salt-call vcf_vcf_services.status_map
salt-call vcf_vcf_services.healthy
```

See [VMSP](../topics/vmsp-mediated.md).
