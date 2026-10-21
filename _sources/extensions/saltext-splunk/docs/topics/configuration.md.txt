(splunk-setup)=
# Configuration
## Execution and state modules
Configure execution and state modules by specifying the name of a configuration
profile in the minion config, minion pillar, or master config. The module
will use the 'splunk' key by default, if defined.

For example:

```yaml
splunk:
    username: alice
    password: abc123
    host: example.splunkcloud.com
    port: 8080
```

## Returner
The returner requires the following config values to be specified in config or pillar:

```yaml
splunk_http_forwarder:
  token: <splunk_http_forwarder_token>
  indexer: <hostname/IP of Splunk indexer>
  sourcetype: <Destination sourcetype for data>
  index: <Destination index for data>
  verify_ssl: true
```
