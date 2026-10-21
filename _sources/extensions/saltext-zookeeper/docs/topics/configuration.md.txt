(zookeeper-setup)=
# Configuration
This Salt extension requires configuration, either in the minion's config file or via the Pillar.

## Basic
```yaml
zookeeper:
  hosts: zoo1,zoo2,zoo3
  default_acl:
    - username: daniel
      password: test
      read: true
      write: true
      create: true
      delete: true
      admin: true
  username: daniel
  password: test
```

## Multiple environments
If configuration for multiple zookeeper environments is required, they can
be set up as different configuration profiles. For example:

```yaml
zookeeper:
  prod:
    hosts: zoo1,zoo2,zoo3
    default_acl:
      - username: daniel
        password: test
        read: true
        write: true
        create: true
        delete: true
        admin: true
    username: daniel
    password: test
  dev:
    hosts:
      - dev1
      - dev2
      - dev3
    default_acl:
      - username: daniel
        password: test
        read: true
        write: true
        create: true
        delete: true
        admin: true
    username: daniel
    password: test
```
