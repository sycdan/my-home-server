---
applyTo: "**/*.proto"
---

# Protobuf Standards (must be followed exactly)

## Schema Mutability

- Adding new fields is always safe
- Never reuse field numbers (critical)
- Reserve deleted field numbers (recommended)
- Never change wiretypes on fields (breaking)

## Coding Style

- Use 2 spaces for indentation, no tabs.
- Limit lines to a maximum of 99 characters.

## Additional Requirements

- Use `edition = "2024"` in all `.proto` files.
  - [More info](https://protobuf.dev/programming-guides/editions/#edition-2024)

## Examples

The following schema will generate a Python class named `ExampleMessage`:

```proto
message ExampleMessage {
  string text = 1;
  int32 value = 2;
}
```
