---
name: api-design
description: Use this when asked to make changes to the API, or reason about surfaces, packages, proto files, adapters or handlers.
---
## The meaning of "surface"

A surface is:

> A versioned **namespace** that defines a coherent API boundary with its own contract, adapter, and handler.

- It is *not* a domain.
- It is *not* an endpoint (it may contain one or many).
- It is *not* a single operation (though it may present like one).

A surface is the unit of versioning.

If you version it, it's a surface; if not, it's not a surface.

That's the whole rule.

## How to identify a surface in a path

A surface is always the entire namespace before the version in a path.

### Examples

- Package: `users/v1`
- Surface: `users`
- Version: `v1`
- Some likely endpoints: GetUser, ListUsers, DeactivateUser

- Package: `internal/devices/execute/v2`
- Surface: `internal/devices/execute`
- Version: `v2`
- Some likely endpoints: ExecuteCommand

- Package: `organization/building/control/v3`
- Surface: `organization/building/control`
- Version: `v3`
- Some likely endpoints: ChangeSetpoint, ResetAlarm

### Why does the surface not include the version?

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

## What files are in a surface package?

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
  tests/devices/execute/v1/test_handler.py
  tests/devices/execute/v1/test_adapter.py
```

The proto file is always named after the last segment of the surface (the leaf) because:

- it keeps filenames short
- it avoids repeating parent namespaces
- it matches the package name
- it keeps codegen paths predictable

So the rule is: `proto/<surface>/<version>/<leaf>.proto`

## How do I add a new endpoint?

To add a new endpoint to `devices/execute/v1`, you:

- Add messages to `proto/devices/execute/v1/execute.proto`
- Regenerate code
- Add handler method
- Add adapter function
- Add tests

You never touch other surfaces.

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
