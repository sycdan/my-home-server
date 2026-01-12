# Today's Task

**Refactor actions.**

## Recommended Pre-reading

Read the `.github` instructions.

Look at [this test](tests/actions/test_create_action.py) to learn about creating actions.

## Goal

All tests

We need to refactor the action system, as it is a bit clunky.

Instead of identifying an action by having it reside in an `/actions/` subdir, let's make it simpler: the presence of a `logic.py` file makes its directory an action.

There should be a 1:1 correspondence with logic files in `./mhs` and `messages.proto` files in `./proto` -- that is, their directory paths should match, as should the package in the proto file. If all this lines up, we can confidently say it's a valid action and it can join our api, to be run via `python call`.

Does that make sense? Let me know if you need clarification.

Briefly summarize the scope of work before proceeding.
