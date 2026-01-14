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

- Use `edition = "2023"` in all `.proto` files.
  - [More info](https://protobuf.dev/programming-guides/editions/#edition-2023)
- Use a `package` path that reflects the domain structure and directory layout:
  - Start with `external` or `internal` to denote the root domain
  - Follow with subdomains as needed
  - End with the action name and version
  - Example: `package internal.new_action.v1;`

## Notes

- Any directory in `proto/` that contains a `contract.proto` file represents an API action.

## Examples

The following schema will generate a Python class named `ExampleMessage`:

```proto
message ExampleMessage {
  string text = 1;
  int32 value = 2;
}
```

Run `./make` to generate code from protobuf definitions.
