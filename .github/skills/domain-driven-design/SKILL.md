---
name: domain-driven-design
description: Use this when asked to make changes to or reason about a domain capability, handler, query, command, action, model or service.
---
## Meaning of "Domain"

A domain is a conceptual boundary -- a slice of the system that represents a stable idea, not a specific instance or a collection of instances. Domains are named with **singular nouns** because they model concepts, not lists.

Domains...

- contain unversioned logic and entities
- evolve independently from API surfaces (which are versioned)
- provide action pathways for users to interact with domain objects

Think of a domain path like `organization.building.device.io` as a chain of nested concepts, each narrowing the scope of meaning. It's not describing "many organizations" or "many buildings" -- it’s describing the conceptual space where this capability lives.

## Meaning of "Capability"

A **capability**...

- is a domain concept (a noun)
- is a cohesive set of domain behaviors centered around a single domain concept
- comprises a set of operations (commands, queries)
- contains services that encapsulate domain logic
- evolves with the domain concept
- applies the Single Responsibility Principle

Capabilities are created automatically when the first action within them is created.

A capability should not exist without at least one action.

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
  models/...         <- persisted domain state
  rules/...          <- pure domain logic (no side effects)
  templates/...      <- shared templates for the whole domain
  errors.py          <- domain-specific exceptions
  <utility>.py       <- domain mechanics (side effects allowed)
  <verb>_<noun>/     <- entrypoint to a domain action
    templates/...    <- optional action-specific templates
    command|query.py <- depends on data access requirements
    errors.py        <- optional domain-specific exceptions
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
from example.domain import loader
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

> "Where is the main CLI entrypoint to a domain, if it has one?"

```python
from example.domain import cli
```
