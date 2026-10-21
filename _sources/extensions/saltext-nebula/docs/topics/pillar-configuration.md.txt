# Pillar Configuration

Nebula network topology and per-host settings are defined in Salt pillar data. This allows centralized management of your mesh network configuration while keeping sensitive data (like IP assignments and firewall rules) separate from states.

## Pillar Structure Overview

The pillar configuration has two main components:

1. **Common settings** - Network-wide configuration (lighthouses, DNS, default firewall rules)
2. **Host settings** - Per-minion configuration (IP address, groups, custom firewall rules)

## Common Configuration

Create `/srv/pillar/nebula/common.sls` for network-wide settings:

```yaml
nebula:
  # Global network settings
  lighthouse_port: 4242          # UDP port for lighthouse communication
  listen_port: 0                 # 0 = random port (recommended for non-lighthouses)
  network_cidr: "10.10.10.0/24"  # Your Nebula network CIDR
  dns_name: "nebula"             # DNS suffix for certificate names

  # Remote allow list - which external networks can reach this node
  remote_allow_list:
    '0.0.0.0/0': true            # Allow IPv4 from anywhere
    '::/0': false                # Disable IPv6 advertisement
    '169.254.0.0/16': false      # Block link-local addresses

  # Lighthouse definitions - your network's coordination points
  lighthouses:
    lighthouse01:
      nebula_ip: "10.10.10.1"
      public_ip: "203.0.113.10"  # Public IP or hostname
    lighthouse02:
      nebula_ip: "10.10.10.2"
      public_ip: "lighthouse02.example.com"

  # Default firewall rules (can be overridden per-host)
  firewall:
    outbound:
      - port: any
        proto: any
        host: any
        description: "Allow all outbound by default"

    inbound:
      - port: any
        proto: icmp
        host: any
        description: "Allow ICMP from any host"
```

### Lighthouse overlay and public addresses

Each entry under `lighthouses` describes how mesh nodes reach a lighthouse. The
module expands these values into Nebula `static_host_map` (overlay address →
list of `public:lighthouse_port` strings) and, on non-lighthouse hosts, into
`lighthouse.hosts` and `relay.relays`.

**`nebula_ip` and `public_ip`** — Each is a string: one address, or several
**comma-separated** addresses. Extra overlay segments add `static_host_map` keys
and `lighthouse.hosts` / `relay.relays` entries; extra public segments add more
`addr:lighthouse_port` values. Every overlay key from `nebula_ip` shares the same
public endpoint list built from `public_ip`.

**IPv6** — Write IPv6 literals in brackets (for example `[2001:db8::1]`) so the
address parses correctly when combined with the UDP port.

Example with dual-stack overlay and public endpoints (comma-separated):

```yaml
  lighthouses:
    lighthouse01:
      nebula_ip: "10.10.10.1,[fd00::1]"
      public_ip: "203.0.113.10,[2001:db8::cafe]"
```

## Host Configuration

Create a pillar file for each host that needs Nebula configuration. For example, `/srv/pillar/nebula/web01.sls`:

```yaml
nebula:
  hosts:
    web01:
      ip: "10.10.10.123/24"      # Nebula IP with CIDR notation
      groups:                     # Security groups for firewall rules
        - "web"
        - "production"
        - "monitoring-target"
      duration: "17532h"          # Certificate validity (2 years)

      # Local allow list - which local interfaces to use
      local_allow_list:
        '0.0.0.0/0': true

      # Host-specific firewall rules (replaces common defaults)
      firewall:
        inbound:
          - port: 22
            proto: tcp
            groups: ["admin"]
            description: "SSH from admin group"

          - port: 80
            proto: tcp
            groups: ["load-balancer"]
            description: "HTTP from load balancers"

          - port: 443
            proto: tcp
            groups: ["load-balancer"]
            description: "HTTPS from load balancers"

          - port: 10050
            proto: tcp
            groups: ["monitoring"]
            description: "Zabbix agent"

          - port: any
            proto: icmp
            host: any
            description: "ICMP from anywhere"

        outbound:
          - port: any
            proto: any
            host: any
            description: "Allow all outbound"
```

## Lighthouse Configuration

Lighthouses require special configuration. Create `/srv/pillar/nebula/lighthouse01.sls`:

```yaml
nebula:
  hosts:
    lighthouse01:
      ip: "10.10.10.1/24"
      is_lighthouse: true         # This node is a lighthouse
      groups:
        - "lighthouse"
        - "infrastructure"
      duration: "43800h"          # Longer validity for infrastructure

      # Lighthouses listen on a fixed port automatically: when is_lighthouse
      # is true, listen.port is pinned to lighthouse_port. Set a per-host
      # listen_port here only to override that (rarely needed).
      # listen_port: 4242

      firewall:
        inbound:
          - port: 4242
            proto: udp
            host: any
            description: "Nebula lighthouse port"

          - port: 22
            proto: tcp
            groups: ["admin"]
            description: "SSH access"

          - port: any
            proto: icmp
            host: any
            description: "ICMP"

        outbound:
          - port: any
            proto: any
            host: any
```

## Pillar Top File

Add the pillar definitions to `/srv/pillar/top.sls`:

```yaml
base:
  # Common settings for all minions
  '*':
    - nebula.common

  # Host-specific configurations
  'web01':
    - nebula.web01

  'web02':
    - nebula.web02

  'lighthouse01':
    - nebula.lighthouse01

  # Or use glob patterns
  'web*':
    - nebula.webservers

  'db*':
    - nebula.databases
```

## Lighthouse DNS

Lighthouses can serve DNS for the Nebula network, allowing hosts to resolve
each other by name. Configure `serve_dns` and the `dns` bind address under
the host entry:

```yaml
nebula:
  hosts:
    lighthouse01:
      ip: "10.10.10.1/24"
      is_lighthouse: true
      serve_dns: true
      dns:
        host: "0.0.0.0"   # bind to all interfaces; use nebula IP to restrict to overlay only
        port: 53           # use a non-privileged port like 5353 if not running as root
```

`serve_dns` is silently ignored for non-lighthouse hosts. Remember to open
the chosen port in the host's inbound firewall rules and in your OS-level
firewall (iptables, nftables, ufw, etc.).

## Nebula SSH Server

Nebula includes a built-in SSH server for management access that operates
independently of the OS SSH daemon. It is disabled by default and only emitted
in the generated config when `enabled: true` is set:

```yaml
nebula:
  hosts:
    myhost:
      ip: "10.10.10.50/24"
      sshd:
        enabled: true
        listen: "127.0.0.1:22"    # address:port for the nebula sshd to bind
        host_key: "/etc/nebula/ssh_host_ed25519_key"  # omit to use this default
        authorized_users:
          - user: alice
            keys:
              - 'ssh-ed25519 AAAA...'
        # Optional: also accept nebula CA-signed SSH certificates
        authorized_nebula_certificate_authorities:
          - 'ssh-ed25519 AAAA...'
```

When `host_key` is omitted it defaults to `<config_dir>/ssh_host_ed25519_key`.
The key file must be generated separately (e.g. `ssh-keygen -t ed25519 -f
/etc/nebula/ssh_host_ed25519_key -N ""`).

## Advanced Configuration Options

### Static Host Map Overrides

The lighthouse ``static_host_map`` is normally derived for every node from the
``lighthouses`` definitions (overlay IP -> ``public_ip:lighthouse_port``). A host
can override or extend it, which is useful when a node should reach a lighthouse
over a different path than the global public endpoint (for example a container
co-located with a lighthouse reaching it on the host bridge instead of hairpinning
the WAN):

```yaml
nebula:
  hosts:
    salt-master:
      ip: "10.10.10.10/24"
      static_host_map:
        # reach lighthouse 10.10.10.1 directly on the local bridge; this
        # replaces the derived public endpoint for that overlay IP
        "10.10.10.1": ["192.0.2.17:4242"]
```

An entry for an overlay IP that is already derived replaces its endpoint list;
an entry for a new overlay IP is added. A common-level ``static_host_map`` may be
used to pin entries for every node.

### Unsafe Routes

Route traffic for external networks through Nebula nodes:

```yaml
nebula:
  hosts:
    gateway01:
      ip: "10.10.10.50/24"
      groups: ["gateway"]
      unsafe_routes:
        - route: "192.168.1.0/24"
          via: "10.10.10.50"
        - route: "172.16.0.0/12"
          via: "10.10.10.50"
```

### Subnets

Assign additional subnet routing to a host:

```yaml
nebula:
  hosts:
    router01:
      ip: "10.10.10.100/24"
      subnets:
        - "192.168.100.0/24"
        - "192.168.200.0/24"
```

### Advertise Addresses

For hosts behind NAT or with multiple interfaces:

```yaml
nebula:
  hosts:
    nat-host:
      ip: "10.10.10.75/24"
      advertise_addrs:
        - "203.0.113.50:4242"
```

### Relay Control

By default a lighthouse also acts as a relay (``am_relay: true``) and every
non-lighthouse uses all lighthouses as its relays. That is a poor fit when a
lighthouse sits behind NAT: it becomes an unreliable relay for the whole mesh.
Three independent controls are available.

Stop a lighthouse from acting as a relay (it still serves discovery), and drop
it from the relay list other nodes build, by marking its ``lighthouses`` entry:

```yaml
nebula:
  lighthouses:
    lighthouse-nat:
      nebula_ip: "10.10.10.1"
      public_ip: "203.0.113.10"
      relay: false        # discovery only, never used as a relay
```

Override ``am_relay`` for a single host regardless of its lighthouse status:

```yaml
nebula:
  hosts:
    lighthouse-nat:
      ip: "10.10.10.1/24"
      is_lighthouse: true
      is_relay: false      # this lighthouse will not relay for others
```

Replace the derived relay list for a host (or, in common, for all hosts) with
an explicit set:

```yaml
nebula:
  hosts:
    web01:
      ip: "10.10.10.123/24"
      relays:
        - "10.10.10.2"     # use only this lighthouse as a relay
```

### Calculated Remotes

For dynamic IP resolution:

```yaml
nebula:
  hosts:
    dynamic-host:
      ip: "10.10.10.80/24"
      calculated_remotes:
        '10.10.10.1':
          - mask: '0.0.0.0/0'
            port: 4242
```

## Overriding Built-in Config Sections

The ``tun``, ``punchy``, ``logging`` and ``conntrack`` sections have sensible
defaults but can be overridden from pillar, at the common level (all nodes) or
per host. Overrides are deep-merged onto the defaults, so you only specify the
keys you want to change:

```yaml
nebula:
  # common: applies to every node
  tun:
    mtu: 1280            # e.g. lower MTU for a WireGuard underlay
  logging:
    level: debug
  conntrack:
    tcp_timeout: "30m"

  hosts:
    web01:
      ip: "10.10.10.123/24"
      punchy:
        delay: "2s"      # per-host override, merged over common + defaults
```

An optional network-wide cipher may be set (it MUST be identical on every node;
do not change it on a live network):

```yaml
nebula:
  cipher: aes            # or chachapoly
```

## Refreshing Pillar Data

After modifying pillar files, refresh the pillar data:

```bash
# Refresh pillar for all minions
salt '*' saltutil.refresh_pillar

# Refresh for specific minions
salt 'web01' saltutil.refresh_pillar

# Verify pillar data
salt 'web01' pillar.get nebula
```

## Pillar Data Validation

Test pillar access from the master:

```bash
# Check what pillar data a minion receives
salt-run nebula.test_pillar_access minion_id=web01
```

This is useful for debugging certificate generation issues.

## Previewing a Host's Generated Config

To see the exact Nebula configuration a minion would receive, rendered from
pillar on the master without contacting the minion:

```bash
# Pretty-print for inspection or diffing
salt-run nebula.show_config minion_id=web01 --out=yaml
```

This is the master-side counterpart to ``salt 'web01' nebula.build_config`` and
produces identical output. The PKI file paths use the standard layout under
``/etc/nebula`` (override with ``config_dir=/path``).

It is also convenient when a single Salt master manages its own Nebula config:
you can render and write the master's config locally without standing up a
second master to highstate it. For example:

```bash
MID=$(salt-call --local grains.get id --out=newline_values_only)
salt-run nebula.show_config minion_id="$MID" --out=yaml > /etc/nebula/nebula.yml
```
