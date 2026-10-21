# Configuration
## General
In order to send a message via Telegram, you need to provide a `chat_id` and a `token`.
If you don't pass them as parameters when calling functions from the execution module,
they need to be defined inside the minion configuration or the pillar.
These configuration values can be specified in either of the following ways:

```yaml
telegram:
  chat_id: '123456789'
  token: '00000000:xxxxxxxxxxxxxxxxxxxxxxxx'
```

```yaml
telegram.chat_id: '123456789'
telegram.token: '00000000:xxxxxxxxxxxxxxxxxxxxxxxx'
```

## Returner

Using the returner module requires the above configuration values
to be set in either the minion configuration or the pillar.
