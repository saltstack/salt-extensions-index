# saltext-bmc

A Salt extension for out-of-band management of bare-metal servers via their BMC
(Baseboard Management Controller). Speaks **Redfish** first and **IPMI** as a
fallback (auto-detected by default), with a uniform interface for:

- power control (on / off / cycle / reset, graceful or forced)
- boot-device override (disk, PXE, UEFI HTTP, BIOS setup, CD, USB — one-shot or persistent)
- inventory (manufacturer, model, serial, UUID, BIOS version, BMC firmware)
- sensors (temperatures, fans, voltages)
- a low-level `bmc_redfish` passthrough for raw GET/POST/PATCH/DELETE against any Redfish endpoint

Primary use case: automated bare-metal provisioning (e.g. UEFI HTTP Boot for ESXi
installs) where Salt needs to power-cycle a host and steer its next boot.
See [`PLAN.md`](PLAN.md) for the full design.

## Install

```bash
pip install saltext.bmc           # Redfish only
pip install 'saltext.bmc[ipmi]'   # adds pyghmi for the IPMI fallback
```

Requires Python ≥ 3.10 and Salt ≥ 3008.

## Quick start

Configure one or more BMC profiles in Pillar:

```yaml
saltext.bmc:
  profiles:
    bmc-host-01:
      host: 10.0.0.5
      username: root
      password: calvin
      verify_ssl: false
      # backend defaults to 'auto' — probes Redfish, falls back to IPMI.
      # Set to 'redfish' or 'ipmi' explicitly to skip the probe.
      # backend: redfish
    legacy-host:
      host: 10.0.0.7
      username: ADMIN
      password: ADMIN
      backend: ipmi
      port: 623          # IPMI-only override
```

Execution module:

```bash
salt-call --local bmc.power_status     bmc-host-01
salt-call --local bmc.set_boot_device  bmc-host-01 device=http persistent=False
salt-call --local bmc.power_cycle      bmc-host-01
salt-call --local bmc.get_system_info  bmc-host-01
salt-call --local bmc.get_sensor_data  bmc-host-01

# Connection kwargs work without a pillar profile:
salt-call --local bmc.power_status host=10.0.0.5 username=root password=calvin verify_ssl=False
```

State module:

```yaml
my-host-boot:
  bmc.boot_device:
    - name: bmc-host-01
    - device: http
    - persistent: false

my-host-power:
  bmc.powered:
    - name: bmc-host-01
    - power: 'on'
```

Low-level Redfish passthrough (Redfish-only profiles):

```bash
salt-call --local bmc_redfish.get   /redfish/v1/ name=bmc-host-01
salt-call --local bmc_redfish.patch /redfish/v1/Systems/1 \
    body='{"AssetTag": "rack-7-slot-3"}' name=bmc-host-01
```

## Resource type

For Salt 3008+ resource-driven workflows, the same operations are exposed as a
`bmc` resource type with per-host targeting:

```yaml
# Pillar
resources:
  bmc:
    bmc-host-01:
      host: 10.10.10.5
      username: root
      password: calvin
      verify_ssl: false
```

```bash
salt  bmc-host-01              bmc_host.power_status   # by resource ID alone
salt -C 'T@bmc:bmc-host-01'    bmc_host.power_status   # by full SRN (type:id)
salt -C 'T@bmc'                bmc_host.power_cycle    # all bmc resources
```

## What's not here

- **Serial-over-LAN console** (`sol`) — SOL is inherently interactive and is
  better served by `ipmitool sol activate` or your BMC's web console. We do not
  ship a `bmc.sol_activate`.
- **IPMI-side `bmc_redfish.*`** — the low-level passthrough is Redfish-only by
  design; it errors immediately if the resolved profile uses `backend: ipmi`.

## License

Apache 2.0
