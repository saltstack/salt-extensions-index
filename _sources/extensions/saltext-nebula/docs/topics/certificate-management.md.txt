# Certificate Management

`saltext-nebula` provides comprehensive certificate lifecycle management, from initial generation through automatic renewal.

## Certificate Generation

Certificates are generated on the Salt master using the `nebula` runner and distributed to minions via the Salt fileserver.

### Manual Generation

Generate a certificate for a specific minion:

```bash
# Generate using pillar configuration
salt-run nebula.get_certificate minion_id=web01

# The certificate is automatically placed in the Salt fileserver
# at salt://nebula/certs/web01.crt and salt://nebula/certs/web01.key
```

The runner reads the minion's configuration from pillar and generates a certificate with:
- The IP address specified in pillar
- Group memberships for firewall rules
- The configured validity duration
- Optional subnet assignments

### Certificate Parameters

Certificate properties are defined in pillar:

```yaml
nebula:
  hosts:
    web01:
      ip: "10.10.10.50/24"         # Required: Nebula IP address
      groups:                       # Optional: Security groups
        - "web"
        - "production"
      subnets:                      # Optional: Routable subnets
        - "192.168.1.0/24"
      duration: "8760h"             # Optional: Validity (default: 720h / 30 days)
```

### Batch Generation

Generate certificates for multiple minions:

```bash
# Using shell loop
for minion in web01 web02 db01 db02; do
    salt-run nebula.get_certificate minion_id=$minion
done

# Or via orchestration
salt-run state.orchestrate orch.generate_certs
```

## Certificate Distribution

Certificates are distributed to minions via the `certificates_present` state.

### Basic Distribution

```yaml
nebula_certificates:
  nebula.certificates_present:
    - name: nebula_certs
```

This state:
1. Checks if certificates exist locally
2. Validates existing certificates against the CA
3. Downloads new certificates from `salt://nebula/certs/` if needed
4. Sets appropriate file permissions
5. Validates the deployed certificate chain

### Distribution Options

```yaml
nebula_certificates:
  nebula.certificates_present:
    - name: nebula_certs_{{ grains['id'] }}
    - minion_id: {{ grains['id'] }}          # Default: current minion
    - cert_dir: /etc/nebula                   # Default: auto-detected
    - force_regenerate: false                 # Force fresh download
    - auto_renew: true                        # Check expiration
    - renewal_threshold_days: 30              # Days before expiry to renew
    - backup_old_certs: true                  # Backup before replacing
    - validate_after_deploy: true             # Verify chain after deployment
```

## Certificate Validation

### Check Certificate Status

```bash
# Comprehensive status check
salt web01 nebula.check_certificate_status

# Output includes:
# - Certificate existence
# - Key existence
# - CA existence
# - Expiration date
# - Days until expiry
# - Validity status
```

### Validate Certificate Chain

```bash
# Verify certificate was signed by the CA
salt web01 nebula.validate_certificate

# Validate specific files
salt web01 nebula.validate_certificate \
    cert_path=/etc/nebula/web01.crt \
    ca_path=/etc/nebula/ca.crt
```

### Parse Certificate Details

```bash
# Get expiration information
salt web01 nebula.parse_cert_expiry cert_path=/etc/nebula/web01.crt
```

## Certificate Renewal

### Manual Renewal

```bash
# Check if renewal is needed
salt web01 nebula.cert_needs_renewal buffer_days=30

# Regenerate on master
salt-run nebula.get_certificate minion_id=web01

# Redeploy to minion
salt web01 state.apply nebula
```

### Automatic Renewal

The `nebula` beacon monitors certificate expiration and fires events when renewal is needed.

#### Configure the Beacon

On minions, add to `/etc/salt/minion.d/beacons.conf`:

```yaml
beacons:
  nebula:
    - interval: 86400              # Check every 24 hours
    - renewal_threshold_days: 30   # Alert when < 30 days remaining
```

Or manage via Salt:

```yaml
configure_nebula_beacon:
  file.managed:
    - name: /etc/salt/minion.d/beacons.conf
    - contents: |
        beacons:
          nebula:
            - interval: 86400
            - renewal_threshold_days: 30
```

#### Beacon Events

When a certificate is within the renewal threshold, the beacon fires:

```
Tag: salt/beacon/web01/nebula/cert/expiring
Data:
  minion_id: web01
  cert_path: /etc/nebula/web01.crt
  days_until_expiry: 25
  expires_at: 2025-02-15T00:00:00
  renewal_threshold_days: 30
  needs_renewal: true
  reason: "Certificate expires in 25 days (within 30 day buffer)"
```

#### Reactor Configuration

Create a reactor to handle renewal events. Add to `/etc/salt/master.d/reactor.conf`:

```yaml
reactor:
  - 'salt/beacon/*/nebula/cert/expiring':
    - /srv/reactor/nebula_renew.sls
```

Create `/srv/reactor/nebula_renew.sls`:

```yaml
# Regenerate certificate on master
regenerate_certificate:
  runner.nebula.get_certificate:
    - minion_id: {{ data['minion_id'] }}

# Trigger state apply on minion
deploy_new_certificate:
  local.state.apply:
    - tgt: {{ data['minion_id'] }}
    - arg:
      - nebula
    - require:
      - runner: regenerate_certificate
```

## Listing Certificates

View all certificates managed by the runner:

```bash
salt-run nebula.list_certificates
```

Output:
```yaml
success: True
total: 5
certificates:
  - minion_id: web01
    cert_path: /etc/nebula/certs/web01.crt
    key_path: /etc/nebula/certs/web01.key
    key_exists: True
    cert_size: 1234
    modified: 2025-01-15T10:30:00
  - minion_id: web02
    ...
```

## Certificate Backup and Rollback

### Automatic Backups

The `certificates_present` state automatically backs up existing certificates:

```yaml
nebula_certificates:
  nebula.certificates_present:
    - backup_old_certs: true  # Default
```

Backups are stored in `<cert_dir>/backups/` with timestamps.

### Manual Backup

```bash
# Create a backup of the current configuration
salt web01 nebula.backup_config
```

### Rollback

If a new certificate causes issues:

```bash
# Restore the last known good configuration
salt web01 nebula.rollback_config
```

## CA Management

### Initialize a New CA

```bash
# Using config defaults
salt-run nebula.ca_init

# With custom options
salt-run nebula.ca_init \
    name="Production Network" \
    duration="87600h" \
    encrypt=True \
    passphrase="secure-passphrase"
```

### Force CA Regeneration

:::{danger}
Regenerating the CA **invalidates all existing certificates**. All nodes will need new certificates.
:::

```bash
salt-run nebula.ca_init force=True
```

### CA Security Best Practices

1. **Always encrypt the CA key** - Use `nebula.ca_encrypt: true`
2. **Secure the passphrase** - Consider using a secrets manager
3. **Restrict CA directory permissions** - `chmod 700 /etc/nebula/ca`
4. **Back up the CA** - Store encrypted backups securely off-system
5. **Monitor CA access** - Audit access to the CA key
