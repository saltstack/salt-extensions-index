The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 1.0.0 (2026-06-07)


### Breaking changes

- Renamed project from ``saltext-vmware`` to ``saltext-vcf``. The PyPI distribution, GitHub repository, and Python import path (``saltext.vmware`` -> ``saltext.vcf``) all change. Salt loader module names also rename from ``vmware_*`` to ``vcf_*`` (e.g. ``vmware_vcenter_appliance`` -> ``vcf_vcenter_appliance``); update any state, pillar, or CLI references accordingly. VMware-defined identifiers (``vmware_accepted`` / ``vmware_certified`` VIB acceptance levels, ``vmware_soap_session`` cookie, ``vmware-api-session-id`` header, ``pyvmomi``, ``vmware-vcenter``/``vmware-vcf`` PyPI dependencies) are unchanged.


### Removed

- Removed the ``installer_credentials``, ``installer_logs``, and ``installer_system`` clients and execution modules. Their ``/v1/system/security/passwords`` / ``/v1/system/log-bundles`` / ``/v1/system/*`` endpoints did not exist on the actual VCF Installer build; ``installer_bringup`` and ``fleet_password`` remain as the verified installer-side surfaces.


### Changed

- ESXi standalone clients (``esxi_advanced``, ``esxi_firewall``, ``esxi_host``, ``esxi_ntp``, ``esxi_service``, ``esxi_syslog``) and ``utils/esxi`` now use pyVmomi SOAP (``SmartConnect`` / ``/sdk``) instead of REST ``/api/session``. Shuttle-deployed lab hosts omit the vAPI endpoint entirely, and ESXi joined to vCenter blocks ``/api/session`` with HTTP 400; SOAP is the universally available surface. The execution-module names and dunder keys (``vcf_esxi_*``) are unchanged.


### Fixed

- Fix several vCenter 9 / VCF 9 REST body shapes discovered against the live lab: ``vcenter_content_library.update_session_add_file`` now uses the path-style ``/api/content/library/item/update-session/{session_id}/file?action=add`` (the legacy POST ``/updatesession/file`` shape 404s on vSphere 9); ``vcenter_content_library.create_local`` / ``create_subscribed`` send the spec at the root (no more ``create_spec`` wrapper); ``vcenter_appliance.dns_set`` / ``logging_forwarding_set`` use PUT (PATCH returns 405); ``sddc_certificates.create_csrs`` sends ``{csrGenerationSpec, resources}`` instead of a flat list.
- VDS and DPG (Distributed Port Group) lifecycle mutators (``vim_dvs.create``/``reconfigure``/``delete``/``add_host``/``remove_host``, ``vim_dvs_portgroup._add``/``reconfigure``/``delete``) now wait on the underlying pyVmomi ``*_Task`` before returning. A shared ``utils/vim.wait_for_task`` helper drives the wait. Previously callers raced the task and ``list_()`` could return a stale view immediately after a successful-looking create.
- ``nsx_ipsec_vpn.create_ike_profile`` / ``create_tunnel_profile`` / ``create_dpd_profile`` now auto-inject the appropriate ``resource_type`` (``IPSecVpnIkeProfile`` / ``IPSecVpnTunnelProfile`` / ``IPSecVpnDpdProfile``) so NSX 9 stops rejecting the PUT with HTTP 400. Callers can still override via ``resource_type=`` in the spec.


### Added

- Added a ``CLI Example:`` doc-example harness: ``tests/_doc_examples`` parses every ``salt '*' <mod>.<func> ...`` line out of module docstrings and exposes them to two passes. ``tests/unit/test_doc_examples`` is a signature-check pass that asserts the virtual module name resolves and the documented args bind to the function. The companion saltext-vcf-integration repo runs the same parsed examples against a live VCF lab.
- Bootstrap the VCF Installer onto a bare ESXi host via pyVmomi OVF deploy. ``clients/ovf_deploy`` adds a tarball-parse + ``OvfManager.CreateImportSpec`` + ``HttpNfcLease`` PUT pipeline (with vmware_soap_session cookie + ``Overwrite: t`` header so ESXi's ha-nfc daemon authorizes the upload), a streaming HTTPS PUT for multi-GB VMDKs, and ``wait_for_task``-driven power-on. State module ``vcf_installer_appliance`` exposes this as a declarative ``installer.running`` workflow.
- New topology + tooling clients: ``automation_topology`` (cross-component view of a VCF Automation deployment), ``installer_topology`` (introspects the bringup spec / running installer), and ``ovftool_deploy`` (subprocess wrapper around ``ovftool`` for callers that prefer it over the pure-pyVmomi path).
- The vCenter per-request HTTP timeout is now configurable. ``utils/vcenter.api_*`` helpers accept an optional ``timeout=`` kwarg; the default is also tunable via the ``saltext.vcf.vcenter.timeout`` pillar key. ``vcenter_content_library.ovf_deploy`` defaults to ``timeout=1800`` (30 min) so OVF deploys no longer race the previous hard-coded 30 s read timeout.
- VCF Automation (VCFA / Aria Automation 9.x) end-to-end integration: new ``utils/vcfa`` with two-step CSP refresh-token auth, per-(host,user) token cache, transparent bearer re-mint on 401, configurable per-request timeout, multipart helper, and a ``wait_for_deployment`` poller. Eighteen new client / execution-module pairs cover cloud accounts, cloud zones, storage profiles, network profiles, projects, project users, cloud templates (blueprint versions), policies, catalog (items + sources), vRO packages, vRO configuration elements, workflow runs, ABX actions, action secrets, action subscriptions, resource actions, IAM role bindings, and custom roles.
- VCF Operations fleet certificate management: new ``vcfops_fleet_certificates`` client + module covering the fleet-wide certificate inventory, renewal scheduling, and rotation operations exposed by VCF Operations (separate from the truststore surface in ``vcfops_certificate``). Contributed by `Denys Aleksandrov <https://github.com/denysaleksandrov>`_.
- VCF Operations fleet password and certificate surfaces: new ``vcfops_fleet_passwords`` (the VCF 9.x replacement for the SDDC-Manager-backed ``fleet_password``) wraps ``/suite-api/api/fleet-management/password-management`` with paginated ``list_``, ``get_account``, ``update``, and a ``check_expiry(threshold_days=90)`` helper that buckets accounts into ``ok`` / ``expiring`` / ``noExpiry`` with ISO-rendered expiry dates. New ``vcfops_certificate`` wraps the VCF Ops truststore (``/suite-api/api/certificate``) for list / get / delete by thumbprint.

## 0.1.0 (2026-05-14)


### Added

- VCF Installer (formerly Cloud Builder) support: utils + clients for system/bringup/credentials/logs, modules, declarative bringup state, plus live lab spin-up/teardown coverage in the integration repo. [#3](https://github.com/salt-extensions/saltext-vcf/issues/3)
