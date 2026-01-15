---
name: domain-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, action, model or service.
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

> Find the last noun before the verb

That noun (`devices`) is the capability.

Everything before the verb is the capability path.

Verbs tend to be like:

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

## Structure

A capability folder contains domain objects & services, plus actions:

```text
scaffolding/
  models/...
  services/...
  create_action/
    templates/...   <- optional
    command.py      <- contains CreateActionCommand
    handler.py      <- implements the command logic
  list_capabilities/
    query.py        <- contains ListCapabilitiesQuery
    handler.py      <- implements the query logic
```

**Example command.py:**

```python
@dataclass
class CreateCapabilityCommand:
  pass
```

**Example query.py:**

```python
@dataclass
class ListCapabilitiesQuery:
  pass
```

## Notes

Capabilities are created automatically when the first action within them is created.

A capability should not exist without at least one action.
