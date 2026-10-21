# State Examples

This page provides complete, production-ready state examples for deploying Nebula with `saltext-nebula`.

## Basic Deployment State

A minimal state for deploying Nebula to a node:

```sls
# /srv/salt/nebula/init.sls

# Deploy certificates from master
nebula_certificates:
  nebula.certificates_present:
    - name: nebula_certs_{{ grains['id'] }}
    - auto_renew: true
    - renewal_threshold_days: 30

# Get detected paths
{% set nebula = salt['nebula.detect_paths']() %}
{% set config = salt['nebula.build_config']() %}

# Ensure config directory exists
nebula_config_dir:
  file.directory:
    - name: {{ nebula.config_dir }}
    - user: {{ nebula.user }}
    - group: {{ nebula.group }}
    - mode: {{ nebula.dir_mode }}
    - makedirs: True

# Generate configuration from pillar
nebula_config:
  file.serialize:
    - name: {{ nebula.config_file }}
    - dataset: {{ config | tojson }}
    - formatter: yaml
    - user: {{ nebula.user }}
    - group: {{ nebula.group }}
    - mode: {{ nebula.file_mode }}
    - require:
      - file: nebula_config_dir

# Enable the service
nebula_service_enable:
  module.run:
    - nebula.service_enable: []

# Restart on changes
nebula_service:
  module.run:
    - nebula.service_restart: []
    - onchanges:
      - file: nebula_config
      - nebula: nebula_certificates
    - require:
      - module: nebula_service_enable
```

## Complete Deployment with Package Installation

A comprehensive state that handles package installation across platforms:

```sls
# /srv/salt/nebula/init.sls

#
# Package Installation
#

{% if grains['os_family'] == 'Debian' %}
nebula_package:
  pkg.installed:
    - name: nebula

{% elif grains['os_family'] == 'RedHat' %}
nebula_package:
  pkg.installed:
    - name: nebula

{% elif grains['os_family'] == 'Alpine' %}
nebula_package:
  pkg.installed:
    - name: nebula

{% elif grains['os'] == 'Windows' %}
nebula_package:
  chocolatey.installed:
    - name: nebula
    - require:
      - chocolatey: chocolatey_bootstrap

chocolatey_bootstrap:
  chocolatey.bootstrapped: []

{% endif %}

#
# User and Group Setup (Linux only)
#

{% if grains['kernel'] != 'Windows' %}
nebula_group:
  group.present:
    - name: nebula
    - system: True

nebula_user:
  user.present:
    - name: nebula
    - system: True
    - gid: nebula
    - home: /etc/nebula
    - shell: /sbin/nologin
    - createhome: False
    - require:
      - group: nebula_group
{% endif %}

#
# Certificate Deployment
#

nebula_certificates:
  nebula.certificates_present:
    - name: nebula_certs_{{ grains['id'] }}
    - minion_id: {{ grains['id'] }}
    - auto_renew: true
    - renewal_threshold_days: 30
    - backup_old_certs: true
    - validate_after_deploy: true
{% if grains['kernel'] != 'Windows' %}
    - require:
      - pkg: nebula_package
      - user: nebula_user
{% else %}
    - require:
      - chocolatey: nebula_package
{% endif %}

#
# Certificate Information Display
#

show_certificate_info:
  nebula.certificate_info:
    - name: cert_info_{{ grains['id'] }}
    - require:
      - nebula: nebula_certificates

#
# Configuration
#

{% set nebula = salt['nebula.detect_paths']() %}
{% set config = salt['nebula.build_config']() %}

nebula_config_dir:
  file.directory:
    - name: {{ nebula.config_dir }}
    - user: {{ nebula.user }}
    - group: {{ nebula.group }}
    - mode: {{ nebula.dir_mode }}
    - makedirs: True

nebula_config_file:
  file.serialize:
    - name: {{ nebula.config_file }}
    - dataset: {{ config | tojson }}
    - formatter: yaml
    - user: {{ nebula.user }}
    - group: {{ nebula.group }}
    - mode: {{ nebula.file_mode }}
    - require:
      - file: nebula_config_dir
      - nebula: nebula_certificates

nebula_config_validate:
  module.run:
    - nebula.validate_config: []
    - onchanges:
      - file: nebula_config_file

#
# TUN Module (Linux only, for containers)
#

{% if grains['kernel'] == 'Linux' and grains.get('virtual', 'physical') != 'physical' %}
tun_module_config:
  file.managed:
    - name: /etc/modules-load.d/tun.conf
    - contents: tun
    - mode: 0644

tun_module_load:
  kmod.present:
    - name: tun
{% endif %}

#
# Service Management
#

nebula_service_enable:
  module.run:
    - nebula.service_enable: []
    - require:
      - file: nebula_config_file

nebula_service:
  module.run:
    - nebula.service_restart: []
    - onchanges:
      - file: nebula_config_file
      - nebula: nebula_certificates
    - require:
      - module: nebula_service_enable
      - module: nebula_config_validate
```

## Lighthouse-Specific State

Additional configuration for lighthouse nodes:

```sls
# /srv/salt/nebula/lighthouse.sls

include:
  - nebula

# Lighthouses need a fixed port in their firewall
{% if grains['os_family'] == 'Debian' %}
lighthouse_firewall:
  ufw.allow:
    - name: nebula-lighthouse
    - proto: udp
    - port: 4242

{% elif grains['os_family'] == 'RedHat' %}
lighthouse_firewall:
  firewalld.present:
    - name: nebula-lighthouse
    - protoports:
      - 4242/udp
{% endif %}
```

## Beacon Configuration State

Deploy the certificate expiration beacon:

```sls
# /srv/salt/nebula/beacon.sls

nebula_beacon_config:
  file.managed:
    - name: /etc/salt/minion.d/nebula-beacon.conf
    - contents: |
        beacons:
          nebula:
            - interval: 86400
            - renewal_threshold_days: 30
    - mode: 0644

restart_minion_for_beacon:
  cmd.run:
    - name: 'salt-call service.restart salt-minion'
    - bg: true
    - onchanges:
      - file: nebula_beacon_config
```

## Orchestration: Generate All Certificates

An orchestration state to generate certificates for all Nebula hosts:

```sls
# /srv/salt/orch/nebula_certs.sls

{% set nebula_hosts = salt.saltutil.runner('pillar.show_pillar', minion='*').get('nebula', {}).get('hosts', {}) %}

{% for host in nebula_hosts %}
generate_cert_{{ host }}:
  salt.runner:
    - name: nebula.get_certificate
    - minion_id: {{ host }}
{% endfor %}
```

Run with:
```bash
salt-run state.orchestrate orch.nebula_certs
```

## Orchestration: Full Deployment

Deploy Nebula to all configured hosts:

```sls
# /srv/salt/orch/nebula_deploy.sls

# First, ensure all certificates are generated
generate_certificates:
  salt.runner:
    - name: state.orchestrate
    - arg:
      - orch.nebula_certs

# Deploy to lighthouses first
deploy_lighthouses:
  salt.state:
    - tgt: 'G@nebula:is_lighthouse:True'
    - tgt_type: compound
    - sls:
      - nebula.lighthouse
    - require:
      - salt: generate_certificates

# Then deploy to all other hosts
deploy_clients:
  salt.state:
    - tgt: 'G@nebula:hosts:*'
    - tgt_type: compound
    - sls:
      - nebula
    - require:
      - salt: deploy_lighthouses

# Verify connectivity
verify_mesh:
  salt.function:
    - name: nebula.test_connectivity
    - tgt: 'G@nebula:hosts:*'
    - tgt_type: compound
    - require:
      - salt: deploy_clients
```

## Cleanup/Removal State

Completely remove Nebula from a system:

```sls
# /srv/salt/nebula/remove.sls

nebula_purge:
  module.run:
    - nebula.purge:
      - remove_package: True
```

Run with:
```bash
salt web01 state.apply nebula.remove
```

## Conditional Deployment Based on Pillar

Only deploy if the minion has Nebula configuration:

```sls
# /srv/salt/nebula/init.sls

{% if salt['pillar.get']('nebula:hosts:' ~ grains['id']) %}

# ... full deployment states ...

{% else %}

nebula_not_configured:
  test.show_notification:
    - text: "No Nebula configuration found for {{ grains['id'] }} in pillar"

{% endif %}
```
