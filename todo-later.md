# Future Tasks (do not implement yet)

We need to build out the local domain actions.

The local domain actions primarily have side effects (if any) for the user's local machine (e.g. creating/updating files), but they can touch remote machines (via ssh) and potentially have side-effects there also.

## Actions

Let's start with `Discover Devices`.

This action will query the router (ssh router '/command') to find devices connected to the LAN, e.g. via the ARP table, and check if they exist in the [fleet config](mhs/config/fleet.textproto). If not, it will add them. It will create or update supplementary ssh config files (**not** in the user's main `.ssh/config`) and update them with the active hostname for that device (static dns name, if available, otherwise IP).

When creating ssh hosts, `Host <MacAddressWithoutColons>` sections will be generated, unless there is a `<name>.lan` hostname for the device, in which case the `<name>` will be used. Newly-created config files will be named `<MacAddressWithoutColons>`.

The user should then be able to ssh to discovered devices.

## Prerequisites

**Important:** do not manually edit textproto -- we need to parse it into python objects, mutate those, then re-export.

## Golden Testing

Add pytest --update-golden or somesuch.