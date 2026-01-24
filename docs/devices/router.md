# MikroTik hEX

Runs [RouterOS](https://help.mikrotik.com/docs/spaces/ROS/pages/328059/RouterOS).

## Setup

Connect cable modem to `ether1` port.

TODO: script to run /ip dns adlist reload -- not sure if we need this; as of 2026-01-18 there were 73838 names (it might auto reload)

### Configure SSH Access

- Log in to RouterOS using [WebFig](http://192.168.1.1)
  - Ensure an A record for `router.lan` exists in IP -> DNS -> Static
  - Initially uses 192.168.88.1; change it to 1.1 (need to change DHCP config also)
- Go to Files -> Upload... and select your SSH public key
- Go to System -> Users -> SSH Keys -> Import SSH Key and add your key to the `admin` user
- Add a host to your local `~/.ssh/config`:

```text
Host router
  HostName router.lan
  User admin
```

### Enable advanced mode

```bash
ssh router '/system device-mode update mode=advanced'
```

Then press the `MODE` button on the side of the router (it will restart automatically).

### Enable DNS for LAN clients

```bash
ssh router '/ip dns set allow-remote-requests=yes'
```

This allows internal clients to resolve `example-service.lan` hostnames.

### Configure Dynamic DNS

Create a system script named `updateDns`:

```bash
{
  :put "Creating DDNS update script"
  /system script remove [find name="ddns-update"]
  /system script add name="ddns-update" comment="Update freedns host with current IP" source="/tool fetch url=\"https://freedns.afraid.org/dynamic/update.php?SmN5TmpQaGhDdG9FQVRNWWEwelk6MjI0MjMyNTg=\" keep-result=no"
  /system script print
  :put "Creating scheduled task"
  /system scheduler remove [find name="ddns"]
  /system scheduler add name="ddns" comment="Keep the Dynamic DNS IP updated" interval="00:30:00" on-event="/system script run ddns-update" disabled=no
  /system scheduler print
}
```

Schedule it to run every 30 minutes.

## Scripting Examples

**Upload and run a one-off script file**:

```bash
scp ./example.rsc router:/
ssh router '/import example.rsc'
```

**Create a system script from a file**:

```bash
scp ./example.rsc router:/
ssh router '/system script add name="example" source=[/file get example.rsc contents]'
```

**Create or update a systems script from a file**:

```bash
ssh router '{:local src [/file get example.rsc contents]; :local sid [/system script find name="example"]; :if ([:len $sid] > 0) do={ /system script set $sid source=$src } else={ /system script add name="example" source=$src }}'
```

**Run a system script**:

```bash
ssh router '/system script run "example"'
```

**Schedule a system script**:

```bash
ssh router '/system scheduler add name="example_schedule" comment="Run example script every 30 minutes" interval="00:30:00" on-event="/system script run \"example\"" disabled=no'
ssh router '/system schedule print'
```

**Delete a schedule**:

```bash
ssh router '/system scheduler remove "example_schedule"'
```

**Delete a system script**:

```bash
ssh router '/system script remove "example"'
```

## [Hardening](https://freedium.cfd/https://medium.com/@muhiminulhasan.me/essential-mikrotik-wan-security-a-beginners-hardening-guide-26e987c5c66a)

Prevents access to various services over WAN.

```bash
{
  :local listName "WAN-GUARD"
  :local wanInterface "ether1"
  :local rules {
    {"tcp,udp"; "21,22,23,443,8080,8291,8728,8729"; "management services"};
    {"tcp,udp"; "33434-33534"; "traceroute probes"};
    {"tcp,udp"; "53"; "DNS requests"};
    {"tcp"; "3128,8080"; "proxy requests"}
    {"udp"; "5678"; "neighbor discovery"};
  }

  # Cleanup
  /ip firewall filter remove [find where in-interface-list="$listName"]
  /interface list member remove [find where list="$listName"]
  /interface list remove [find where name="$listName"]
  
  # Create and populate our list
  /interface list add name="$listName" comment="Protects listed interfaces from WAN-based attacks"
  /interface list member add interface="$wanInterface" list="$listName"

  # Additional config
  /ip neighbor discovery-settings set discover-interface-list="!$listName"
  /ip proxy set enabled=no

  # Create firewall rules
  :foreach rule in=$rules do={
    :local protocols ($rule->0)
    :local ports ($rule->1)
    :local description ($rule->2)
    
    :if ($protocols~"tcp") do={
      /ip firewall filter add action=drop chain=input protocol=tcp dst-port="$ports" in-interface-list="$listName" comment="Deny access to $description (TCP)"
    }
    :if ($protocols~"udp") do={
      /ip firewall filter add action=drop chain=input protocol=udp dst-port="$ports" in-interface-list="$listName" comment="Deny access to $description (UDP)"
    }
  }
  /ip firewall filter print
}
```

## Ad Blocking

Block ads network-wide using the adlist feature. This method redirects ad domains to a null IP.

```bash
{
  /ip dns set cache-size 204800
  /ip dns adlist add url="https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts" ssl-verify=no
}
```

### Port Forwarding

```bash
{
  # Cleanup
  /ip firewall nat remove [find where comment~"[MHS]"]
  
  # Forward WAN port 80/443 to reverse proxy
  # Reverse proxy discovers its own IP via DNS update
  # so these rules use static DNS lookup at runtime
  
  /ip firewall nat add \
    comment="Ingress HTTP [MHS]" \
    chain=dstnat \
    in-interface=ether1 \
    protocol=tcp \
    dst-port=80 \
    action=dst-nat \
    to-addresses=[/ip dns static get [find name="reverse-proxy.lan"] address] \
    to-ports=80
  
  /ip firewall nat add \
    comment="Ingress HTTPS [MHS]" \
    chain=dstnat \
    in-interface=ether1 \
    protocol=tcp \
    dst-port=443 \
    action=dst-nat \
    to-addresses=[/ip dns static get [find name="reverse-proxy.lan"] address] \
    to-ports=443
  
  # Hairpin NAT for internal clients
  /ip firewall nat add \
    comment="Hairpin Ingress [MHS]" \
    chain=srcnat \
    src-address=192.168.1.0/24 \
    protocol=tcp \
    dst-port=80 \
    action=src-nat \
    to-addresses=192.168.1.1
  /ip firewall nat add \
    comment="Hairpin Ingress HTTPS [MHS]" \
    chain=srcnat \
    src-address=192.168.1.0/24 \
    protocol=tcp \
    dst-port=443 \
    action=src-nat \
    to-addresses=192.168.1.1
}
/ip firewall nat print where comment~"[MHS]"
```
