---
name: domain-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, model or service.
---
## Meaning of "Capability"

A domain capability is a cohesive set of domain behaviors centered around a single domain concept.

You could also call it a domain **slice**.

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
