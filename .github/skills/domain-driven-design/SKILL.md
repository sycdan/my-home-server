---
name: domain-driven-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, action, model or service.
---
## Meaning of "Capability"

A **capability**...

- is a domain concept (a noun)
- is a cohesive set of domain behaviors centered around a single domain concept
- comprises a set of operations (commands, queries)
- contains services that encapsulate domain logic
- evolves with the domain concept
- applies the Single Responsibility Principle

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
/<domain>/
  engine/...         <- runtime mechanics (side effects allowed)
  models/...         <- persisted domain state
  rules/...          <- pure domain logic (no side effects)
  templates/...      <- shared templates for the whole domain
  <verb>_<noun>/     <- entrypoint to a domain action
    templates/...    <- optional action-specific templates
    command|query.py <- depends on data access requirements
    handler.py       <- implements the action logic
```

**Example command.py:**

```python
@dataclass
class CreateCapabilityCommand:
  pass
```

When using HTTP/1.1, commands must be invoked using the POST method.

**Example query.py:**

```python
@dataclass
class ListCapabilitiesQuery:
  pass
```

When using HTTP/1.1, commands may be invoked using either POST or GET methods (POST is required for sufficiently large queries).

## Notes

Capabilities are created automatically when the first action within them is created.

A capability should not exist without at least one action.

## FAQ

> "Where does validation logic live?"

```python
from example.domain.rules import validation
```

> "Where are naming conventions defined?"

```python
from example.domain.rules import naming
```

> "What if I need to load modules dynamically?"

```python
from example.domain.engine import loader
```

> "Where is the shape of a read-only action defined?"

```python
from example.domain.<verb_noun>.query import <VerbNoun>Query
```

> "Where is the shape of a read-write or write-only action defined?"

```python
from example.domain.<verb_noun>.command import <VerbNoun>Command
```

> "Where is an action's logic defined?"

```python
from example.domain.<verb_noun>.handler import handle_<verb_noun>
```

> "Where do I put domain models?"

```python
from example.domain import models
```

> "Where do I put runtime helpers or execution context?"

```python
from example.domain.engine import runtime
```
