# Master Configuration

The Salt master requires configuration to manage the Nebula Certificate Authority and generate certificates for minions.

## Runner Configuration

Create `/etc/salt/master.d/nebula.conf` to configure the nebula runner:

```yaml
# Path configuration
nebula.cert_dir: /etc/nebula/certs        # Where generated certificates are stored
nebula.ca_key: /etc/nebula/ca/ca.key      # CA private key location
nebula.ca_crt: /etc/nebula/ca/ca.crt      # CA certificate location
nebula.salt_cert_dir: /srv/salt/nebula/certs  # Salt fileserver location for cert distribution

# CA configuration
nebula.ca_name: "My Nebula Network"       # Name embedded in the CA certificate
nebula.ca_duration: "87600h"              # CA validity (default: 10 years)
nebula.ca_encrypt: true                   # Encrypt the CA private key
nebula.ca_passphrase: "your-secure-passphrase"  # Required if ca_encrypt is true
```

### Configuration Options

| Option                 | Default                       | Description                                       |
|------------------------|-------------------------------|---------------------------------------------------|
| `nebula.cert_dir`      | `/etc/nebula/certs`           | Directory for generated host certificates         |
| `nebula.ca_key`        | `/etc/nebula/ca/ca.key`       | Path to CA private key                            |
| `nebula.ca_crt`        | `/etc/nebula/ca/ca.crt`       | Path to CA certificate                            |
| `nebula.salt_cert_dir` | `/srv/salt/nebula/certs`      | Salt fileserver path for certificate distribution |
| `nebula.ca_name`       | `Salt Managed Nebula Network` | CA certificate name                               |
| `nebula.ca_duration`   | `87600h`                      | CA certificate validity period                    |
| `nebula.ca_encrypt`    | `false`                       | Whether to encrypt the CA private key             |
| `nebula.ca_passphrase` | `None`                        | Passphrase for encrypted CA key                   |

:::{warning}
If `nebula.ca_encrypt` is `true`, you **must** set `nebula.ca_passphrase`. Certificate signing operations will fail without it.
:::

## Directory Setup

Create the required directories with appropriate permissions:

```bash
# CA directory (restricted access)
mkdir -p /etc/nebula/ca
chmod 700 /etc/nebula/ca

# Generated certificates directory
mkdir -p /etc/nebula/certs
chmod 750 /etc/nebula/certs

# Salt fileserver directory for distribution
mkdir -p /srv/salt/nebula/certs
chmod 755 /srv/salt/nebula/certs
```

## Initializing the CA

After configuration, initialize the Certificate Authority:

```bash
# Initialize with default settings from config
salt-run nebula.ca_init

# Or specify options directly
salt-run nebula.ca_init name="Production Nebula" duration="43800h" encrypt=True passphrase="secure-phrase"
```

This creates:
- `ca.crt` - The CA certificate (distributed to all nodes)
- `ca.key` - The CA private key (kept secure on the master)

The CA certificate is automatically copied to the Salt fileserver location for minion retrieval.

:::{danger}
**Protect your CA private key!** Anyone with access to the CA key can issue valid certificates for your mesh network. Use encryption (`ca_encrypt: true`) and secure the passphrase appropriately.
:::

## Applying Configuration

After creating or modifying the configuration, restart the Salt master:

```bash
# systemd
systemctl restart salt-master

# OpenRC
rc-service salt-master restart
```
