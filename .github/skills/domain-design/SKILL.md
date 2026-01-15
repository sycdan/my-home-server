---
name: domain-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, model or service.
---
## Meaning of "Capability"

A domain capability is a cohesive set of domain behaviors centered around a single domain concept.

## General rule for extracting capabilities from paths

Given a domain path like: `a.b.c.d`

Use this rule:

- Drop namespaces (a, internal, organization, etc.)
- Find the last noun before the verb
- That noun is the capability
- The final segment (verb) is the action

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

A capability folder contains the domain model, domain services, and the set of actions (commands/queries + handlers) that operate on that domain concept.

```text
domain-name/
  models.py
  services.py
  errors.py
  create/
    commands.py
    handlers.py
  list/
    queries.py
    handlers.py
  delete/
    commands.py
    handlers.py
```
