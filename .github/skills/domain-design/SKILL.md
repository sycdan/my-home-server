---
name: domain-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, model or service.
---
## Meaning of "Capability"

A **capability**...

- is a domain concept (a noun)
- is a cohesive set of domain behaviors centered around a single domain concept
- comprises a set of operations (commands, queries)
- contains services that encapsulate domain logic

In our application, `scaffolding` is a **capability** (and *also* a domain).

## General rule for extracting capabilities from paths

Given a domain path like: `internal.network.devices.execute`

Use this rule:

- Drop namespaces (`internal.network`)
- Find the last noun before the verb

That noun (`devices`) is the capability.

### How to detect the verb

Verbs tend to be:

```text
audit
configure
create
delete
execute
export
get
import
list
monitor
provision
render
reporting
sync
update
```

Everything before the verb is the capability path.

## Structure

A capability folder contains actions:

```text
scaffolding/
  utils.py
  create_api/
    command.py
    handler.py
  create_capability/
    command.py
    handler.py
  list_capabilities/
    query.py
    handler.py
```
