# Cross-Platform Support

`saltext-nebula` is designed to work across different operating systems and installation methods. The extension automatically detects the platform and adapts paths, service management, and permissions accordingly.

## Path Detection

The `detect_paths` function automatically identifies your Nebula installation:

```bash
salt '*' nebula.detect_paths
```

Example output for a Linux package installation:
```yaml
binary_path: /usr/bin/nebula
cert_binary_path: /usr/bin/nebula-cert
config_dir: /etc/nebula
cert_dir: /etc/nebula
config_file: /etc/nebula/nebula.yml
backup_dir: /etc/nebula/backups
ca_file: /etc/nebula/ca.crt
cert_file: /etc/nebula/web01.crt
key_file: /etc/nebula/web01.key
service_name: nebula
install_method: package
user: root
group: nebula
file_mode: '0640'
dir_mode: '0750'
path_sep: /
```

### Platform-Specific Paths

#### Linux Package Installation
```
binary:     /usr/bin/nebula or /usr/sbin/nebula
config:     /etc/nebula/nebula.yml
certs:      /etc/nebula/
service:    nebula (systemd or OpenRC)
```

#### Linux Snap Installation
```
binary:     /snap/bin/nebula
config:     /var/snap/nebula/common/config/config.yaml
certs:      /var/snap/nebula/common/certs/
service:    nebula (snap service)
```

#### Windows Chocolatey
```
binary:     C:\ProgramData\chocolatey\bin\nebula.exe
config:     C:\ProgramData\Nebula\nebula.yml
certs:      C:\ProgramData\Nebula\
service:    nebula (Windows Service)
```

#### Windows GitHub Release
```
binary:     C:\Program Files\Nebula\nebula.exe
config:     C:\ProgramData\Nebula\nebula.yml
certs:      C:\ProgramData\Nebula\
service:    nebula (Windows Service)
```

## Service Management

Service operations are abstracted to work across init systems:

```bash
# Works on systemd, OpenRC, snap, and Windows
salt '*' nebula.service_restart
salt '*' nebula.service_status
salt '*' nebula.service_enable
```

### Platform-Specific Commands

Behind the scenes, these map to:

| Action  | systemd                      | OpenRC                      | Snap                         | Windows                               |
|---------|------------------------------|-----------------------------|------------------------------|---------------------------------------|
| restart | `systemctl restart nebula`   | `rc-service nebula restart` | `snap restart nebula`        | `net stop nebula && net start nebula` |
| status  | `systemctl is-active nebula` | `rc-service nebula status`  | `snap services nebula`       | `sc query nebula`                     |
| enable  | `systemctl enable nebula`    | `rc-update add nebula`      | `snap start --enable nebula` | `sc config nebula start= auto`        |

## Writing Cross-Platform States

The execution module handles platform differences, allowing states to remain simple:

```sls
# This state works on Linux, Windows, Alpine, etc.
{% set nebula = salt['nebula.detect_paths']() %}
{% set config = salt['nebula.build_config']() %}

nebula_config:
  file.serialize:
    - name: {{ nebula.config_file }}
    - dataset: {{ config | tojson }}
    - formatter: yaml
    - user: {{ nebula.user }}
    - group: {{ nebula.group }}
    - mode: {{ nebula.file_mode }}
```

### Platform-Specific Overrides

When you need platform-specific behavior, use grains:

```sls
{% if grains['os_family'] == 'Windows' %}
nebula_package:
  chocolatey.installed:
    - name: nebula

{% elif grains['os_family'] == 'Debian' %}
nebula_package:
  pkg.installed:
    - name: nebula

{% elif grains['os_family'] == 'Alpine' %}
nebula_package:
  cmd.run:
    - name: apk add nebula
    - unless: which nebula

{% endif %}
```

## File Permissions

Permissions are handled appropriately for each platform:

### Unix Systems

```yaml
# Execution module returns appropriate defaults
file_mode: '0640'   # Certificates readable by group
dir_mode: '0750'    # Directories accessible by group
user: root
group: nebula
```

### Windows Systems

Windows doesn't use Unix-style permissions. The state module uses `icacls` to set ACLs:

- Private keys: SYSTEM and Administrators only (Full Control)
- Certificates: SYSTEM, Administrators (Full Control), Users (Read)

## Pillar Overrides

You can override detected paths via pillar if needed:

```yaml
nebula:
  config_dir: /opt/nebula/config
  cert_dir: /opt/nebula/certs
  binary_path: /opt/nebula/bin/nebula
  cert_binary_path: /opt/nebula/bin/nebula-cert
  service_name: my-nebula
```

## Troubleshooting Platform Issues

### Detection Problems

If paths aren't detected correctly:

```bash
# View what was detected
salt web01 nebula.detect_paths

# Check what binaries exist
salt web01 cmd.run 'which nebula nebula-cert'  # Linux
salt web01 cmd.run 'where nebula.exe'           # Windows
```

### Service Issues

```bash
# Check service status
salt web01 nebula.service_status

# View service details (Linux systemd)
salt web01 cmd.run 'systemctl status nebula'

# View service details (Windows)
salt web01 cmd.run 'sc query nebula'
```

### Permission Issues

```bash
# Check file ownership (Linux)
salt web01 cmd.run 'ls -la /etc/nebula/'

# Check ACLs (Windows)
salt web01 cmd.run 'icacls C:\ProgramData\Nebula'
```
