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

Think of a domain path like `organization.building.device.io` as a chain of nested concepts, each narrowing the scope of meaning. It's not describing "many organizations" or "many buildings" -- it’s describing the conceptual space where each capability lives.

## Meaning of "Capability"

A **capability**...

- is a domain subsystem
- is a cohesive set of domain behaviors centered around a single domain concept
- comprises a set of operations (commands, queries)
- contains services that encapsulate domain logic
- evolves with the domain concept
- applies the Single Responsibility Principle
- should not exist without at least one action
- is created automatically when the first action within it is created

**Example:**

```text
cyberdyne/           <- domain
  skynet/            <- domain
    defense/         <- capability
      fire_nukes/    <- action
        command.py   <- action shape
        handler.py   <- execution logic
```

### General rule for extracting capabilities from paths

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

### Structure

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

An action package folder looks like:

```text
<domain>/<capability>/<action>/
  __init__.py
  command.oy or query.py
  handler.py
```

Entities live at the domain level as stable nouns; capabilities are functional subsystems; actions are verbs; and the final segment of any action path must always be the action.

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

## Meaning of "Stable Entity"

A **stable** entity...

- is a *simple* entity
- exists in a domain has no exposed actions
- is not *capable*

In REST terms, it is a **resource**.

**Example:**

```text
cyberdyne/           <- domain
  skynet/            <- domain
    weapon/          <- capability
      nuke/          <- entity
        entity.py    <- entity shape
        rules.py     <- validation logic
```

## Meaning of "Capable Entity"

A **capable** entity...

- is a *complex* entity
- exists in a domain and exposes one or more actions
- is a **resource controller** in REST terms

**Example:**

```text
cyberdyne/           <- domain
  skynet/            <- domain
    nuke/            <- capable entity
      entity.py      <- entity shape
      arm/           <- action
        command.py   <- action shape
        handler.py   <- execution logic
      disarm/        <- action
        command.py   <- action shape
        handler.py   <- execution logic
      status/        <- action (read-only)
        query.py     <- action shape
        handler.py   <- execution logic
      fire/          <- action
        command.py   <- action shape
        handler.py   <- execution logic
```

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
