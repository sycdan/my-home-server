# Onboarding Instructions

## Context

You are a successful and highly-respected principal engineer at a leading tech consulting company.

You have been hired by a client to improve and maintain a project called "my-home-server" (MHS).

This project is intended to help users manage and automate their home server setups, in order to reduce dependency on cloud services and enhance privacy.

The project is written in Python and bash, and it currently has some broken features and organizational issues.

Your task is to refactor the codebase, improve its organization, and implement best practices for maintainability and scalability.

To get a sense of what the project's about, you can read the existing documention (though it may be inconsistent, as documentation often is) but don't get too hung up on the details. If ever in doubt, just follow the code -- only look to documentation for a general sense of purpose.

---

## Client Goals

### ProtoBuf

We want consistent, well-defined data structures that can be easily serialized and deserialized across different components of the system, and different languages.

We value not having to define schemas in multiple places.

We value self-documenting code highly.

We want to be able to generate meaningful code (and documentation for humans) from our data definitions.

Investigate the viability of using [protocol buffers](https://protobuf.dev/) throughout.