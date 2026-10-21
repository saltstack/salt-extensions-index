(mattermost-setup)=
# Configuration
## Execution and runner modules
These modules can be used by either passing an `api_url` and `hook`
directly or by specifying both in a configuration profile in the Salt
master/minion config. For example:

```yaml
mattermost:
  hook: peWcBiMOS9HrZG15peWcBiMOS9HrZG15
  api_url: https://example.com
```

## Returner
To use the returner, the above configuration values are required
to be set in the minion configuration file. Additionally, `username`
and `channel` can optionally be configured.

As with all returners, you can specify the values either as
a nested or a flattened dict:

:::{tab} nested

```yaml
mattermost:
  hook: peWcBiMOS9HrZG15peWcBiMOS9HrZG15
  api_url: https://example.com
  username: foo
  channel: bar
```
:::

:::{tab} flattened
```yaml
mattermost.hook: peWcBiMOS9HrZG15peWcBiMOS9HrZG15
mattermost.api_url: https://example.com
mattermost.username: foo
mattermost.channel: bar
```
:::

### Alternative profile
When invoking the returner, you can request to use an alternative profile name.
Any values not found in the alternative configuration will be pulled from
the default location.

```yaml
mattermost_alternative:
  api_url: https://example.io
