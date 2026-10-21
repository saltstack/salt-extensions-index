# Configuration

(influxdb08-setup)=
## `influxdb08` execution/state modules
This module accepts connection configuration details either as
parameters or as configuration settings in /etc/salt/minion on the relevant
minions:

```yaml
influxdb08.host: 'localhost'
influxdb08.port: 8086
influxdb08.user: 'root'
influxdb08.password: 'root'
```

This data can also be passed into pillar. Options passed into opts will
overwrite options passed into pillar.

(influxdb-setup)=
## `influxdb` execution/state modules
This module accepts connection configuration details either as
parameters or as configuration settings in /etc/salt/minion on the relevant
minions:

```yaml
influxdb.host: 'localhost'
influxdb.port: 8086
influxdb.user: 'root'
influxdb.password: 'root'
```

This data can also be passed into pillar. Options passed into opts will
overwrite options passed into pillar.

(influxdb-returner-setup)=
## 'influxdb' returner
### Default profile
Configure the following parameters in the minion or master config
(shown values are the defaults):

```yaml
influxdb.db: 'salt'
influxdb.user: 'salt'
influxdb.password: 'salt'
influxdb.host: 'localhost'
influxdb.port: 8086
```

### Alternative profile
Alternative configuration values can be used by prefixing the configuration.
Any values not found in the alternative configuration will be pulled from
the default location:

```yaml
alternative.influxdb.db: 'salt'
alternative.influxdb.user: 'salt'
alternative.influxdb.password: 'salt'
alternative.influxdb.host: 'localhost'
alternative.influxdb.port: 6379
```
