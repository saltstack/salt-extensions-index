# Dynamic IP Allocation

`saltext-nebula` can assign each minion a stable Nebula overlay IP automatically,
so a new node joins the mesh without a hand-written `ip` in pillar. Allocation is
handled by the `nebula_ipam` external pillar, which runs on the master and
injects the address at `nebula:hosts:<minion_id>:ip`. Because certificate signing
and config assembly already read the address from that exact location, nothing
downstream changes.

## How it works

The ext_pillar assigns the lowest free address from a configured pool the first
time it sees a minion, records it in a SQLite database on the master, and returns
the same address on every subsequent pillar compile. The allocation is stable for
the life of the node, which matters because changing it would invalidate the
minion's signed certificate.

Allocation is deliberately conservative:

- A minion that already has an explicit `ip` in pillar is left untouched. Static
  assignments keep working, and dynamic allocation is purely opt-in.
- Lighthouse overlay addresses, every statically assigned host IP, and any
  operator `reserve` entries are excluded from the pool, so a dynamic address can
  never collide with a pinned one.
- Allocation runs inside a `BEGIN IMMEDIATE` SQLite transaction with a `UNIQUE`
  constraint on the address. Parallel pillar compilations across master worker
  threads cannot hand out the same IP twice.
- A minion with no `nebula` pillar at all is skipped entirely, so only mesh nodes
  are allocated addresses.

## Configuration

Add the ext_pillar to the master config:

```yaml
ext_pillar:
  - nebula_ipam:
      network: 10.10.10.0/24
      pool: 10.10.10.10-10.10.10.250
      store: /etc/nebula/ipam.sqlite
```

| Option                | Description |
|-----------------------|-------------|
| `network`             | Overlay network in CIDR form (required). Its prefix length formats allocated addresses, e.g. `10.10.10.42/24`. |
| `pool`                | Optional `start-end` range limiting which addresses are handed out. Defaults to the network's usable host range. Required for large or IPv6 networks. |
| `store`               | Path to the SQLite database. Default: `/etc/nebula/ipam.sqlite`. |
| `reserve`             | Optional list of individual addresses to exclude. |
| `reserve_lighthouses` | Exclude lighthouse overlay addresses found in pillar. Default: `true`. |
| `pillar_key`          | Top-level pillar key holding the Nebula config. Default: `nebula`. |

The injected `ip` merges into the minion's existing host entry, so keys such as
`groups` and `duration` are preserved. This relies on Salt's default recursive
pillar merge (`pillar_source_merging_strategy: smart`, the default).

## Minimal frictionless host

With the allocator configured, adding a node to the mesh can be as little as
assigning the shared `nebula` pillar via the top file. No per-host block is
required:

```yaml
nebula:
  hosts:
    web01:
      groups:
        - web
```

`web01` receives an overlay IP automatically. If a host does not deviate from the
global mesh definition, even the `groups` list can be omitted and the node still
gets an address and a working certificate.

## Managing allocations

The runner exposes admin operations against the same store. The store path
defaults to `nebula.ipam_store` in the master config, which should match the
`store` set for the ext_pillar.

```bash
# List every allocation, ordered by address
salt-run nebula.ipam_list

# Show one minion's allocation
salt-run nebula.ipam_show minion_id=web01

# Release an allocation when decommissioning a node
salt-run nebula.ipam_release minion_id=web01
```

Releasing frees the address for reuse. Reusing an address while a previously
issued certificate for it is still valid is risky, so release only after the old
certificate has been revoked or has expired.

## End-to-end: allocate, sign, deploy

Allocation is implicit in pillar compilation. `nebula.get_certificate` calls
`pillar.show_pillar` on the master, which runs the `nebula_ipam` ext_pillar and
assigns the address before the certificate is signed with it. There is no
separate "allocate" call to make: compiling the minion's pillar is what
allocates, and every path that reads the pillar triggers it.

For a single host the sequence is:

```bash
# Compiling the pillar assigns the address; show_config previews the result.
salt-run nebula.show_config minion_id=web01
salt-run nebula.ipam_show minion_id=web01      # confirm the assigned address

# Sign the certificate. This compiles the pillar again (idempotent: the same
# address is returned) and signs with it.
salt-run nebula.get_certificate minion_id=web01

# Deploy certificates, config and service to the minion.
salt web01 state.apply nebula
```

### Orchestration

Initialize the CA once as a prerequisite:

```bash
salt-run nebula.ca_init
```

Then this orchestration allocates, signs and deploys across the whole mesh. It
targets minions by a `roles:nebula` grain; adjust the target to however you
assign the `nebula` pillar (grain, nodegroup, or pillar match).

```sls
# /srv/salt/orch/nebula_deploy.sls

{% set nebula_minions = salt.saltutil.runner(
     'manage.up', tgt='roles:nebula', tgt_type='grain') %}

# 1. Allocate an overlay IP (transparently, via the nebula_ipam ext_pillar) and
#    sign each minion's certificate with it. get_certificate compiles the
#    minion's pillar, which is what performs the allocation, so no separate
#    allocate step is needed.
{% for minion in nebula_minions %}
nebula_cert_{{ minion }}:
  salt.runner:
    - name: nebula.get_certificate
    - minion_id: {{ minion }}
{% endfor %}

# 2. Surface the resulting allocations for review before deploying.
nebula_ipam_report:
  salt.runner:
    - name: nebula.ipam_list
    - require:
      {% for minion in nebula_minions %}
      - salt: nebula_cert_{{ minion }}
      {% endfor %}

# 3. Deploy certificates, config and service to the minions.
nebula_deploy:
  salt.state:
    - tgt: 'roles:nebula'
    - tgt_type: grain
    - sls:
      - nebula
    - require:
      - salt: nebula_ipam_report

# 4. Verify mesh connectivity.
nebula_verify:
  salt.function:
    - name: nebula.test_connectivity
    - tgt: 'roles:nebula'
    - tgt_type: grain
    - require:
      - salt: nebula_deploy
```

Run it with:

```bash
salt-run state.orchestrate orch.nebula_deploy
```

Because allocation is allocate-once, the orchestration is safe to re-run: hosts
that already hold an address keep it, and only genuinely new minions are
assigned one. A frictionless host that has only the shared `nebula` pillar (no
per-host block) is allocated an address and signed on its first pass with no
extra configuration.
