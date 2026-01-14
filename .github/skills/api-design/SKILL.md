---
name: api-design
description: Use this when asked to make changes to the API, or reason about surfaces, packages, proto files, adapters or handlers.
---
## The Meaning of "Surface"

A **surface** is a versioned **namespace** that defines a coherent API boundary with its own contract, adapter, and handler.

- It is *not* a domain.
- It is *not* an endpoint (it may contain one or many).
- It is *not* a single operation (though it may present like one).

If you version it, it's a surface; if not, it's not a surface.

That's it.

## How to Identify a Surface in a Path

A surface is always the entire namespace before the version in a path.

### Examples

```yaml
package: users/v1
surface: users
version: v1
endpoints: GetUser, ListUsers, DeactivateUser
```

```yaml
package: internal/devices/execute/v2
surface: internal/devices/execute
version: v2
endpoints: ExecuteCommand
```

```yaml
package: organization/building/control/v3
surface: organization/building/control
version: v3
endpoints: ChangeSetpoint, ResetAlarm
```

You may ask:

> "Why does the surface not include the version?"

Because versioning applies to the entire surface, not individual endpoints.

When you bump from v1 to v2, you're saying:

> "This entire namespace has changed in a way that breaks compatibility."

That's why the version folder sits inside the surface folder.

## Plural vs Singular Surfaces

Surfaces are namespaces, not domain entities.

So the plural/singular rule is simple:

Use plural when the surface represents a resource family, e.g.:

- users/v1
- devices/v1
- reports/v2
- permissions/v1

This matches REST, gRPC, and most API conventions.

Use singular when the surface represents an operation family, e.g.:

- sync/v1
- execute/v1
- search/v1
- ingest/v1
- export/v1

These are verbs, not nouns -- and verbs don't pluralize.

Use whatever the namespace naturally is when it's nested, e.g.:

- internal/devices/execute/v1
- public/analytics/reports/v2
- admin/users/permissions/v1

**The rule is:**

Pluralize nouns. Don't pluralize verbs.

That's it.

## API Package Contents

Given:

```yaml
surface: devices/execute
version: v1
```

Then:

```yaml
leaf: execute
```

And your files lives at:

```yaml
proto: proto/devices/execute/v1/execute.proto
adapter: api/devices/execute/v1/adapter.py
handler: api/devices/execute/v1/handler.py
tests: |
  tests/devices/execute/v1/test_adapter.py
  tests/devices/execute/v1/test_handler.py
```

The proto file is always named after the last segment of the surface (the leaf) because:

- it keeps filenames short
- it avoids repeating parent namespaces
- it matches the package name
- it keeps codegen paths predictable

So the rule is: `proto/<surface>/<version>/<leaf>.proto`

## How to Add an Endpoint

To add a new endpoint to `devices/execute/v1`, you:

- add messages to `proto/devices/execute/v1/execute.proto` (e.g. Request & Response)
- regenerate code
- add handler method
- add adapter functions
- add tests

You never touch other surfaces.

## When to Add a Surface

Create a new surface when:

- the namespace is new
- the versioning lifecycle is independent
- the conceptual grouping is distinct
- the interaction pattern is distinct
- the exposure model is different
- the proto file is becoming too large (try to keep under 1000 LOC)

Otherwise, add the endpoint to an existing surface.

## How to Add a New Surface

To add billing/payments/v1, you create:

```text
proto/billing/payments/v1/payments.proto
api/billing/payments/v1/handler.py
api/billing/payments/v1/adapter.py
tests/billing/payments/v1/test_adapter.py
tests/billing/payments/v1/test_handler.py
```

Done.

## Summary of the Rules (the cheat sheet)

- Plural nouns -> resource surfaces
  - users, devices, reports

- Singular verbs -> operation surfaces
  - sync, execute, search, ingest

- Surfaces represent interaction boundaries, not domains
  - Domains stay noun‑based and unversioned

- The proto file is named after the last segment of the surface
  - proto/<surface>/<version>/<leaf>.proto

- Surfaces can be nested
  - internal/devices/execute/v1

- Each surface gets its own versioned folder
  - Never mix surfaces
