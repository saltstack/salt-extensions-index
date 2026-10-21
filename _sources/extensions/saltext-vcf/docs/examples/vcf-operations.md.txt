# VCF Operations examples

## Inventory + adapters

```bash
salt-call vcf_vcfops_version.get
salt-call vcf_vcfops_adapter.list_
salt-call vcf_vcfops_resource.list_ page=0 page_size=100
salt-call vcf_vcfops_resource.get <resource-uuid>
salt-call vcf_vcfops_resource.relationships <resource-uuid>
salt-call vcf_vcfops_resource.stats <resource-uuid>
```

## Alerts + symptoms

```bash
salt-call vcf_vcfops_alert.active_list page_size=50
salt-call vcf_vcfops_alert.active_list resourceId=<uuid> activeOnly=true
salt-call vcf_vcfops_alert.alerts_list page_size=100
salt-call vcf_vcfops_alert.symptoms_list page_size=100
salt-call vcf_vcfops_recommendation.list_ page_size=10
```

## Policies + notifications

```bash
salt-call vcf_vcfops_policy.list_
salt-call vcf_vcfops_policy.get <policy-id>
salt-call vcf_vcfops_policy.notification_rules_list
```

## RBAC

```bash
salt-call vcf_vcfops_auth.sources_list
salt-call vcf_vcfops_auth.roles_list
salt-call vcf_vcfops_auth.users_list
salt-call vcf_vcfops_auth.usergroups_list
salt-call vcf_vcfops_auth.privileges_list
```

```yaml
User:
  vcf_vcfops_user.present:
    - name: alice
    - password: '{{ pillar['ops_alice_password'] }}'
    - first_name: Alice
    - last_name: Operator
    - email: alice@example.com
    - role_names: [Administrator]

Custom role:
  vcf_vcfops_role.present:
    - name: ReadOnlyMonitor
    - display_name: "Read-only Monitor"
    - description: "View-only access for monitoring agents"
    - privilege_keys: [DASHBOARD, METRICS_DASHBOARDS, ALERTS_VIEW]
```

System-defined roles can't be deleted; `vcf_vcfops_role.absent`
no-ops on them.

## Collectors

```bash
salt-call vcf_vcfops_collector.list_
salt-call vcf_vcfops_collector.groups_list
salt-call vcf_vcfops_collector.groups_create \
    group_spec='{"name":"primary","collectorId":[12345]}'
```

## Credentials

```bash
salt-call vcf_vcfops_credential.kinds_list
salt-call vcf_vcfops_credential.list_
```

```yaml
Register vCenter credentials:
  vcf_vcfops_credential.present:
    - name: vc-prod
    - adapter_kind: VMWARE
    - credential_kind: PRINCIPALCREDENTIAL
    - fields:
        - name: USER
          value: administrator@vsphere.local
        - name: PASSWORD
          value: '{{ pillar['ops_vc_password'] }}'
```

## Super metrics

```bash
salt-call vcf_vcfops_supermetric.list_ page_size=20
```

```yaml
Rolling-average CPU:
  vcf_vcfops_supermetric.present:
    - name: rolling-avg-cpu
    - formula: 'avg(${this, metric=cpu|usage_average})'
    - description: 7-day rolling average CPU
```

## Resource groups

```bash
salt-call vcf_vcfops_resource_group.list_

salt-call vcf_vcfops_resource_group.create \
    group_spec='{"resourceKey":{"name":"prod-vms","adapterKindKey":"VMWARE","resourceKindKey":"VirtualMachine"}, "membershipDefinition":{"includedResources":[]}}'
```

## Reports

```bash
salt-call vcf_vcfops_report.list_ page_size=20

salt-call vcf_vcfops_report.generate \
    report_spec='{"resourceId":"<uuid>","reportDefinitionId":"<uuid>"}'

salt-call vcf_vcfops_report.download <report-id> fmt=PDF
```

## Maintenance schedules

```bash
salt-call vcf_vcfops_maintenance.list_
salt-call vcf_vcfops_maintenance.create '{"name":"weekly", ...}'
```

## Tasks

```bash
salt-call vcf_vcfops_task.get <task-id>
salt-call vcf_vcfops_task.list_ page_size=20
```

## Solutions

```bash
salt-call vcf_vcfops_solution.list_
salt-call vcf_vcfops_solution.get <solution-id>
```

## Node status

```bash
salt-call vcf_vcfops_deployment.node_status
salt-call vcf_vcfops_deployment.healthy
salt-call vcf_vcfops_deployment.applications_list
```
