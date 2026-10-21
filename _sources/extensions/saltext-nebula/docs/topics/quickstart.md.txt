# Quick Start Guide

This guide walks you through setting up a basic Nebula mesh network with `saltext-nebula`. By the end, you'll have a working mesh with one lighthouse and one client node.

## Prerequisites

- A working Salt master/minion infrastructure
- `nebula-cert` binary installed on the Salt master
- Nebula package installed on target minions
- Network connectivity between nodes (UDP port 4242 by default)

## Step 1: Install the Extension

On the Salt master:

```bash
salt-pip install saltext-nebula
```

On all minions that will join the mesh:

```bash
salt '*' pip.install saltext-nebula
# Or use a state for consistent deployment
```

## Step 2: Configure the Master

Create `/etc/salt/master.d/nebula.conf`:

```yaml
# Nebula runner configuration
nebula.cert_dir: /etc/nebula/certs
nebula.ca_key: /etc/nebula/ca/ca.key
nebula.ca_crt: /etc/nebula/ca/ca.crt
nebula.salt_cert_dir: /srv/salt/nebula/certs

# CA settings
nebula.ca_name: "My Nebula Network"
nebula.ca_duration: "87600h"
nebula.ca_encrypt: true
nebula.ca_passphrase: "change-this-to-a-secure-passphrase"
```

Create the required directories:

```bash
mkdir -p /etc/nebula/ca /etc/nebula/certs /srv/salt/nebula/certs
chmod 700 /etc/nebula/ca
```

Restart the Salt master:

```bash
systemctl restart salt-master
```

## Step 3: Create Pillar Configuration

Create `/srv/pillar/nebula/common.sls`:

```yaml
nebula:
  lighthouse_port: 4242
  listen_port: 0
  network_cidr: "10.10.10.0/24"
  dns_name: "nebula"

  remote_allow_list:
    '0.0.0.0/0': true
    '::/0': false

  lighthouses:
    lighthouse01:
      nebula_ip: "10.10.10.1"
      public_ip: "YOUR_LIGHTHOUSE_PUBLIC_IP"  # Replace with actual IP
```

Create `/srv/pillar/nebula/lighthouse01.sls`:

```yaml
nebula:
  hosts:
    lighthouse01:
      ip: "10.10.10.1/24"
      is_lighthouse: true
      groups:
        - "lighthouse"
        - "infrastructure"
      duration: "43800h"

      firewall:
        inbound:
          - port: 4242
            proto: udp
            host: any
          - port: any
            proto: icmp
            host: any
        outbound:
          - port: any
            proto: any
            host: any
```

Create `/srv/pillar/nebula/client01.sls`:

```yaml
nebula:
  hosts:
    client01:
      ip: "10.10.10.10/24"
      groups:
        - "clients"
      duration: "8760h"

      firewall:
        inbound:
          - port: any
            proto: icmp
            host: any
        outbound:
          - port: any
            proto: any
            host: any
```

Update `/srv/pillar/top.sls`:

```yaml
base:
  '*':
    - nebula.common
  'lighthouse01':
    - nebula.lighthouse01
  'client01':
    - nebula.client01
```

Refresh pillar data:

```bash
salt '*' saltutil.refresh_pillar
```

## Step 4: Initialize the CA

```bash
salt-run nebula.ca_init
```

Expected output:
```
success: True
ca_crt: /etc/nebula/ca/ca.crt
ca_key: /etc/nebula/ca/ca.key
name: My Nebula Network
duration: 87600h
encrypted: True
```

## Step 5: Generate Certificates

```bash
# Generate certificate for the lighthouse
salt-run nebula.get_certificate minion_id=lighthouse01

# Generate certificate for the client
salt-run nebula.get_certificate minion_id=client01
```

## Step 6: Create the Deployment State

Create `/srv/salt/nebula/init.sls`:

```sls
# Ensure Nebula is installed (adjust for your OS)
nebula_package:
  pkg.installed:
    - name: nebula

# Deploy certificates from master
nebula_certificates:
  nebula.certificates_present:
    - name: nebula_certs_{{ grains['id'] }}
    - auto_renew: true
    - renewal_threshold_days: 30
    - backup_old_certs: true
    - validate_after_deploy: true

# Get installation paths
{% set nebula = salt['nebula.detect_paths']() %}
{% set config = salt['nebula.build_config']() %}

# Ensure config directory exists
nebula_config_dir:
  file.directory:
    - name: {{ nebula.config_dir }}
    - mode: 0750
    - makedirs: True

# Generate configuration from pillar
nebula_config:
  file.serialize:
    - name: {{ nebula.config_file }}
    - dataset: {{ config | tojson }}
    - formatter: yaml
    - mode: 0640
    - require:
      - file: nebula_config_dir

# Validate the configuration
nebula_validate:
  module.run:
    - nebula.validate_config: []
    - onchanges:
      - file: nebula_config

# Enable and manage the service
nebula_service_enable:
  module.run:
    - nebula.service_enable: []

nebula_service:
  module.run:
    - nebula.service_restart: []
    - onchanges:
      - file: nebula_config
      - nebula: nebula_certificates
    - require:
      - module: nebula_service_enable
```

## Step 7: Deploy

Apply the state to your nodes:

```bash
# Deploy to lighthouse first
salt lighthouse01 state.apply nebula

# Then deploy to clients
salt client01 state.apply nebula
```

## Step 8: Verify Connectivity

Test that the mesh is working:

```bash
# Check certificate status
salt '*' nebula.check_certificate_status

# Test connectivity to lighthouse
salt client01 nebula.test_connectivity

# Or ping from the lighthouse
salt lighthouse01 nebula.test_connectivity target_host=10.10.10.10
```

## Troubleshooting

### Certificate Issues

```bash
# Check certificate details
salt web01 nebula.check_certificate_status

# Validate certificate chain
salt web01 nebula.validate_certificate

# Force certificate regeneration
salt-run nebula.get_certificate minion_id=web01
salt web01 state.apply nebula
```

### Service Issues

```bash
# Check service status
salt web01 nebula.service_status

# View detected paths
salt web01 nebula.detect_paths

# Manually restart
salt web01 nebula.service_restart
```

### Pillar Issues

```bash
# Verify pillar data
salt web01 pillar.get nebula

# Test pillar access from master
salt-run nebula.test_pillar_access minion_id=web01

# Refresh pillar
salt web01 saltutil.refresh_pillar
```

## Next Steps

- Read the [Pillar Configuration](pillar-configuration.md) guide for advanced topology options, including multiple overlay and public addresses (IPv4, IPv6, and dual-stack).
- Set up [Automatic Certificate Renewal](certificate-management.md) with beacons
- Review the [Module Reference](../ref/modules/index) for all available functions
