# NSX examples

Policy API (`/policy/api/v1/`) and Management API (`/api/v1/`) share
the `nsx` pillar block.

## Policy API — networking

```bash
salt-call vcf_nsx_segment.list_
salt-call vcf_nsx_segment.get my-segment
salt-call vcf_nsx_segment.create my-segment \
    transport_zone_path=/infra/sites/default/enforcement-points/default/transport-zones/<tz-id> \
    subnets='[{"gateway_address":"10.0.0.1/24"}]'

salt-call vcf_nsx_tier0.list_
salt-call vcf_nsx_tier1.create my-t1 display_name=my-t1

salt-call vcf_nsx_ip_block.list_
salt-call vcf_nsx_ip_pool.list_
salt-call vcf_nsx_edge_cluster.list_
salt-call vcf_nsx_dhcp.list_server_configs
```

## Policy API — DFW

```bash
salt-call vcf_nsx_group.list_
salt-call vcf_nsx_security_policy.list_
salt-call vcf_nsx_firewall_rule.list_ security_policy_id=default-layer3-section
salt-call vcf_nsx_service.list_
salt-call vcf_nsx_context_profile.list_
```

## Policy API — NAT

```bash
# Tier-1
salt-call vcf_nsx_nat.list_ t1=my-t1
salt-call vcf_nsx_nat.create snat-out my-t1 \
    action=SNAT source_network=10.0.0.0/24 translated_network=192.168.1.1
salt-call vcf_nsx_nat.delete snat-out my-t1

# Tier-0
salt-call vcf_nsx_nat.list_t0 t0=my-t0
```

## Management API — node, cluster, fabric

```bash
salt-call vcf_nsx_node.info
salt-call vcf_nsx_cluster.status
salt-call vcf_nsx_transport_zone.list_
salt-call vcf_nsx_transport_node.list_
salt-call vcf_nsx_compute_collection.list_
```

## Management API — RBAC

```bash
salt-call vcf_nsx_role_binding.list_
salt-call vcf_nsx_role_binding.create \
    spec='{"name":"alice","type":"remote_user","roles":[{"role":"auditor"}]}'
```

## States

```yaml
Security policy:
  vcf_nsx_security_policy.present:
    - name: my-policy
    - rules: []

Firewall rule:
  vcf_nsx_firewall_rule.present:
    - name: allow-web
    - security_policy_id: my-policy
    - action: ALLOW
    - source_groups: [/infra/domains/default/groups/web]
    - destination_groups: [/infra/domains/default/groups/db]
    - services: [/infra/services/HTTPS]
```
