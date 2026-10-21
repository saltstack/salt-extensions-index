# VCF Automation (VCFA) integration

VCF Automation 9.x exposes the former Aria Automation / vRA 8.x API
surface, rebranded and bundled with the VCF platform. This document
maps every area the saltext provides to its underlying VCFA endpoint,
explains the shared auth flow, and lists the decisions taken when
the integration originally landed.

## Auth

Two-step bearer-token flow, identical to vRA/Aria 8.x:

```
POST /csp/gateway/am/api/login          # refresh-token acquire
     {"username": "...", "password": "...", "domain": "System Domain"}
  -> {"refresh_token": "..."}

POST /iaas/api/login                    # bearer exchange
     {"refreshToken": "..."}
  -> {"token": "<bearer>"}

Authorization: Bearer <bearer>          # on every subsequent call
```

`saltext.vcf.utils.vcfa` caches the `(refresh_token, bearer)` pair
per `(host, username)`. On 401 the bearer is re-minted from the
cached refresh token; only when that fails does the CSP login get
re-hit.

## Pillar

```yaml
saltext.vcf:
  vcfa:
    host: automation.vcf.example.com
    username: configadmin
    password: secret
    domain: System Domain         # optional; default "System Domain"
    verify_ssl: false
    timeout: 60                   # optional; default 30
```

Long-running calls (catalog requests, OVF deploys, workflow runs)
return quickly with an async job id. `utils.vcfa.wait_for_deployment`
polls `/deployment/api/deployments/{id}` until terminal — use it when
you need to block on completion.

## Service surfaces

VCFA is several microservices behind a common gateway, each rooted at
its own path. `utils.vcfa` doesn't prepend a base path; callers pass
the full `/<service>/api/...` path.

| Service        | Prefix              | Modules                                                                                                                                            |
|----------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| IaaS           | `/iaas/api`         | `cloud_account`, `cloud_zone`, `storage_profile`, `network_profile`, `project`, `project_user`                                                     |
| Blueprint      | `/blueprint/api`    | `cloud_template`                                                                                                                                   |
| Catalog        | `/catalog/api`      | `catalog`                                                                                                                                          |
| Policy         | `/policy/api`       | `policy`                                                                                                                                           |
| ABX            | `/abx/api`          | `action`, `action_secret`                                                                                                                          |
| Event broker   | `/event-broker/api` | `action_subscription`                                                                                                                              |
| Form service   | `/form-service/api` | `resource_action`                                                                                                                                  |
| vRO            | `/vco/api`          | `vro_package`, `vro_config_element`, `workflow_run`                                                                                                |
| CSP / IAM      | `/csp/gateway/am/api`, `/iam/api` | `iam`, `custom_role`                                                                                                                  |
| Deployment     | `/deployment/api`   | (consumed by `utils.vcfa.wait_for_deployment`)                                                                                                     |

## Module index

| Area | Client | Execution module | Key operations |
|------|--------|------------------|----------------|
| Cloud accounts | `vcfa_cloud_account` | `vcf_vcfa_cloud_account` | list, get, create_vsphere, update_vsphere, create_nsxt, update_nsxt, delete, regions |
| Cloud zones | `vcfa_cloud_zone` | `vcf_vcfa_cloud_zone` | list, get, create, update, delete, computes |
| Storage profiles | `vcfa_storage_profile` | `vcf_vcfa_storage_profile` | list, list_vsphere, get, get_vsphere, create_vsphere, update_vsphere, delete |
| Network profiles | `vcfa_network_profile` | `vcf_vcfa_network_profile` | list, get, create, update, delete |
| Projects | `vcfa_project` | `vcf_vcfa_project` | list, get, create, update, delete, resources |
| Project users | `vcfa_project_user` | `vcf_vcfa_project_user` | list_members, add_member (idempotent), remove_member (idempotent), set_members |
| Cloud templates | `vcfa_cloud_template` | `vcf_vcfa_cloud_template` | list, get, create, update, delete + versions: list_versions, get_version, create_version, release_version, unrelease_version |
| Policies | `vcfa_policy` | `vcf_vcfa_policy` | list, get, create, update, delete, list_types |
| Catalog | `vcfa_catalog` | `vcf_vcfa_catalog` | list_items, get_item, request_item, sources: list/get/create/update/delete |
| vRO packages | `vcfa_vro_package` | `vcf_vcfa_vro_package` | list, get, import_, delete, export_ |
| vRO config elements | `vcfa_vro_config_element` | `vcf_vcfa_vro_config_element` | list, get, create, update, delete, get_attribute, set_attribute |
| Workflow runs | `vcfa_workflow_run` | `vcf_vcfa_workflow_run` | list, get, start, cancel, logs, state |
| ABX actions | `vcfa_action` | `vcf_vcfa_action` | list, get, create, update, delete, run, list_runs |
| ABX action secrets | `vcfa_action_secret` | `vcf_vcfa_action_secret` | list, get, create, update, delete |
| Action subscriptions | `vcfa_action_subscription` | `vcf_vcfa_action_subscription` | list, get, create, update, delete, list_event_topics |
| Resource actions | `vcfa_resource_action` | `vcf_vcfa_resource_action` | list, get, create, update, delete |
| IAM | `vcfa_iam` | `vcf_vcfa_iam` | list_orgs, get_org, list_users, get_user_roles, patch_user_roles |
| Custom roles | `vcfa_custom_role` | `vcf_vcfa_custom_role` | list, get, create, update, delete |

## Design decisions

These were the choices taken when the integration originally landed
in a single PR. Each is reversible — bias toward changing the call
sites and updating this doc rather than living with a wrong default.

1. **Multipart helper lives in `utils/vcfa`.**
   Only the vRO package import needs multipart today. If a second
   util ends up needing it the helper can move to a shared
   `utils/_http.py` then.
2. **Resource actions and ABX actions are separate clients.**
   They're distinct VCFA surfaces (`/form-service/api/custom/resource-actions`
   vs `/abx/api/resources/actions`) and serve different use cases —
   resource actions are day-2 operations on a deployed resource;
   ABX actions are reusable functions invoked from blueprints,
   subscriptions, or on-demand.
3. **IAM scope is role bindings only.**
   `vcfa_iam` exposes user / org / role-binding management at
   `/csp/gateway/am/api/orgs/...`. Org-level SSO/domain configuration
   lives behind a different CSP surface and is out of scope here.
4. **Policy uses `/policy/api/policies`.**
   The IaaS service also exposes a handful of policy endpoints; the
   central policy service is canonical in 9.x and covers every
   `typeId` we currently care about.
5. **`wait_for_deployment` is the catalog/deploy waiter.**
   Lives in `utils.vcfa`; polls
   `/deployment/api/deployments/{id}` until terminal
   (`*_SUCCESSFUL` or `*_FAILED`). Used by callers that synchronously
   want the result of a catalog request.
6. **Execution modules only, no state modules.**
   This PR lands the execution layer. Salt state modules
   (`*.present` / `*.absent`) for the configuration-style areas
   (cloud_account, project, policy, action, etc.) come in a follow-up
   so the execution surface can settle before declarative shape
   gets baked on top.

## Out of scope

- Day-2 deployment operations beyond what's reachable through
  `vcfa_action` / `vcfa_resource_action` / `vcfa_workflow_run`
  (e.g. resize VM, attach disk).
- Property groups (`/properties-ui/api/...`).
- Code Stream (`/pipeline/api/...`).
- A separate Service Broker surface — catalog covers it.
