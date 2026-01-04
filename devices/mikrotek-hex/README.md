# Mikrotek hEX

Ethernet `router`. Cable modem connects to `ether1`.

Administer RouterOS using [WebFig](http://192.168.1.1) or SSH.

All scripts are idempotent (unless otherwise noted) and should be run from a terminal.

## Prerequisites

### Device Mode

Device mode must be set to advanced from a terminal:

```bash
/system device-mode update mode=advanced
```

Then press the `MODE` button on the side of the router (it will restart automatically).

### SSH Access

- Go to Files and upload your SSH public key.
- Go to System -> Users -> SSH Keys and add your key.

## DHCP

Uses `192.168.1.*`.

## Routing by hostname

This will allow you to make requests to machines on your LAN by name instead of IP, e.g. `ssh my-home-server`.

```bash
/ip dns set allow-remote-requests=yes
/ip dhcp-server set 0 use-dns=yes
```


## Static IPs

Addresses below *.*.*.10 are reserved for networking hardware, e.g. routers.

```bash
{
  :local leases {
    {"192.168.1.3"; "B8:27:EB:AB:C0:DC"; "Raspberry Pi 3 (ethernet)"}
    {"192.168.1.4"; "B8:27:EB:FE:95:89"; "Raspberry Pi 3 (wireless)"}
    {"192.168.1.10"; "A8:A1:59:F1:3E:B5"; "HTPC"}
    {"192.168.1.11"; "00:23:5A:1A:A4:F6"; "Old Lenovo Laptop (ethernet)"}
    {"192.168.1.12"; "00:1E:65:3B:C7:94"; "Old Lenovo Laptop (wireless)"}
    {"192.168.1.13"; "9C:6B:00:3F:C3:CA"; "Dan's PC (ethernet)"}
    {"192.168.1.14"; "84:A9:38:0E:9C:2F"; "Dan's Laptop (ethernet)"}
    {"192.168.1.15"; "B4:B5:B6:7D:0D:D9"; "Dan's Laptop (wireless)"}
    {"192.168.1.16"; "82:D2:FB:C2:12:5C"; "Dan's iPhone (wireless)"}
    {"192.168.1.22"; "70:85:C2:4F:35:AB"; "Nicole's PC"}
    {"192.168.1.23"; "00:E0:4C:65:4D:53"; "Nicole's Laptop"}
    {"192.168.1.24"; "50:20:65:3F:12:7C"; "Nicole's Steam Deck (wireless)"}
  }
  :foreach lease in=$leases do={
    :local ip ($lease->0)
    :local mac ($lease->1)
    :local name ($lease->2)
    :local shouldAdd 0
    
    # Check if lease exists for this MAC
    :local existing [/ip dhcp-server lease find mac-address=$mac]
    :if ([:len $existing] > 0) do={
      :local existingIp [/ip dhcp-server lease get $existing address]
      :put "$mac currently leases $existingIp"
      :if ($existingIp != $ip) do={
        :put "Remapping $mac to $ip"
        /ip dhcp-server lease remove $existing
        :set shouldAdd 1
      }
    } else={
      :put "No lease for $mac"
      :set shouldAdd 1
    }

    :if ($shouldAdd = 1) do={
      :put "Creating lease for $mac -> $ip"
      /ip dhcp-server lease add address=$ip mac-address=$mac comment=$name
    }
  }
}
/ip dhcp-server lease print
```

## Static IPs with Failover

Maps devices with multiple network interfaces to a single IP. Automatically uses the most recently seen interface. Run periodically (e.g., every 5 minutes) to handle interface changes.

Go to System -> Scripts -> New and paste this:

```bash
{
  :local devices {
    {
      "name"="Raspberry Pi 3";
      "ip"="192.168.1.3";
      "macs"={
        {"B8:27:EB:AB:C0:DC"; "ethernet"};
        {"B8:27:EB:FE:95:89"; "wireless"};
      }
    };
    {
      "name"="Old Lenovo Laptop";
      "ip"="192.168.1.11";
      "macs"={
        {"00:23:5A:1A:A4:F6"; "ethernet"};
        {"00:1E:65:3B:C7:94"; "wireless"};
      }
    };
    {
      "name"="Dan's PC";
      "ip"="192.168.1.13";
      "macs"={
        {"9C:6B:00:3F:C3:CA"; "ethernet"};
      }
    };
    {
      "name"="Dan's Laptop";
      "ip"="192.168.1.14";
      "macs"={
        {"84:A9:38:0E:9C:2F"; "ethernet"};
        {"B4:B5:B6:7D:0D:D9"; "wireless"};
      }
    };
  }

  :foreach device in=$devices do={
    :local deviceName ($device->"name")
    :local targetIp ($device->"ip")
    :local interfaces ($device->"macs")
    :put "Determining best MAC for $deviceName ($targetIp)"
    :foreach interface in=$interfaces do={
      :put $interface
    }
  }
}
/ip dhcp-server lease print

  :foreach device in=$devices do={
    :local deviceName ($device->"name")
    :local targetIp ($device->"ip")
    :local macs ($device->"macs")
    :log debug "Determining best MAC for $deviceName ($targetIp)"
    
    :local newestMac ""
    :local newestName ""
    :local newestTime ""
    :put "Checking $deviceName"
    
    # Find the most recently leased MAC
    :foreach macEntry in=$macs do={
      :local mac ($macEntry->0)
      :local macName ($macEntry->1)
      :local lease [/ip dhcp-server lease find mac-address=$mac]
      :if ([:len $lease] > 0) do={
        :local lastSeen [/ip dhcp-server lease get $lease last-seen]
        :local currentIp [/ip dhcp-server lease get $lease address]
        :put "  [$macName] $mac at $currentIp (seen: $lastSeen)"
        
        # Prefer any interface that has been seen, then pick the most recent
        :if ($lastSeen != "never") do={
          :if ($newestTime = "" || $newestTime = "never") do={
            :set newestMac $mac
            :set newestName $macName
            :set newestTime $lastSeen
            :put "    -> This is the active interface"
          }
        } else if ($newestTime = "") do={
          :set newestMac $mac
          :set newestName $macName
          :set newestTime $lastSeen
        }
      }
    }
    
    # Update the lease mapping if needed
    :if ($newestMac != "") do={
      :local lease [/ip dhcp-server lease find mac-address=$newestMac]
      :local currentIp [/ip dhcp-server lease get $lease address]
      
      :if ($currentIp != $targetIp) do={
        :put "  Remapping $deviceName [$newestName] to $targetIp"
        /ip dhcp-server lease set $lease address=$targetIp
      } else={
        :put "  $deviceName [$newestName] already at $targetIp"
      }
    } else={
      :put "  WARNING: No active lease found for $deviceName"
    }
  }
}

```

**Setup:** Create a scheduled task to run this periodically:

```bash
/system scheduler add name="static-ips-failover" \
  comment="Update device IPs based on most recent interface" \
  interval="00:05:00" \
  on-event="[paste the script above]" \
  disabled=no
```

## Port Forwarding

Supports both WAN and LAN access via the same URL (e.g., `home.sycdan.com:50002`). Hairpin NAT allows internal clients to reach services via external domain.

```bash
{
  /ip firewall nat remove [find where comment~"\\[MHS\\]"]
  
  :local services {
    {"Jellyfin on HTPC"; "50001"; "192.168.1.10"; "8096"}
    {"Immich on Old Lenovo Laptop"; "50002"; "192.168.1.11"; "2283"}
  }
  
  :foreach service in=$services do={
    :local name ($service->0)
    :local extPort ($service->1)
    :local intAddr ($service->2)
    :local intPort ($service->3)
    
    /ip firewall nat add comment="$name [MHS]" \
      chain=dstnat action=dst-nat \
      in-interface=ether1 protocol=tcp dst-port=$extPort \
      to-addresses=$intAddr to-ports=$intPort
    /ip firewall nat add comment="$name (Hairpin) [MHS]" \
      chain=srcnat action=src-nat \
      src-address=192.168.1.0/24 protocol=tcp dst-port=$intPort \
      dst-address=$intAddr to-addresses=192.168.1.1
  }
}
/ip firewall nat print
```

**Note:** Internal clients must resolve `home.sycdan.com` to your router's WAN IP.

## Dynamic DNS

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

TODO: script to run /ip dns adlist reload

## Ingress

Traffic routing is handled by a reverse proxy on [[devices/raspberry-pi/README]].

### Split DNS (Internal Access)

Internal LAN clients resolve ingress domains to the reverse proxy. Uses the most recently seen reverse proxy IP:

```bash
{
  :local services {
    {"photos.sycdan.com"}
    {"stream.sycdan.com"}
  }
  
  # Define which lease names provide the reverse proxy IPs
  :local rpNames {
    "Raspberry Pi 3 (ethernet)"
    "Raspberry Pi 3 (wireless)"
  }

  :local selectedIp "192.168.1.4"

  # TODO: Find the most recently seen RP
  # :local selectedIp ""
  # :local newestTime ""
  # :foreach name in=$rpNames do={
  #   :local lease [/ip dhcp-server lease find comment=$name]
  #   :if ([:len $lease] > 0) do={
  #     :local ip [/ip dhcp-server lease get $lease address]
  #     :local lastSeen [/ip dhcp-server lease get $lease last-seen]
  #     :put "Found $name at $ip (last seen: $lastSeen)"
      
  #     # Prefer any interface that has been seen over one that hasn't ("never")
  #     # If both have been seen, pick the most recent
  #     :if ($lastSeen != "never") do={
  #       :if ($newestTime = "" || $newestTime = "never") do={
  #         :set selectedIp $ip
  #         :set newestTime $lastSeen
  #         :put "  -> Using this IP (first active)"
  #       }
  #     } else if ($newestTime = "") do={
  #       :set selectedIp $ip
  #       :set newestTime $lastSeen
  #       :put "  -> Using this IP (no active interface yet)"
  #     }
  #   } else={
  #     :put "WARNING: Could not find lease for $name"
  #   }
  # }

  # Cleanup
  /ip dns static remove [find comment~"[MHS]"]

  # Configure DNS entries using selected IP
  :foreach service in=$services do={
    :local domain ($service->0)
    :put "Forwarding $domain -> $selectedIp"
    /ip dns static add name=$domain address=$selectedIp comment="Internal Ingress Proxy [MHS]"
  }

  :put "Split DNS configuration complete"
  /ip dns static print where comment~"[MHS]"
}
```

### Port Forwarding alt

```bash
{
  # Cleanup
  /ip firewall nat remove [find where comment~"[MHS]"]
  
  :local rpis {
    {"192.168.1.3"; "ethernet"}
    {"192.168.1.4"; "wireless"}
  }
  
  :foreach rpi in=$rpis do={
    :local addr ($rpi->0)
    :local iface ($rpi->1)
    
    # Forward WAN port 80 to Raspberry Pi
    /ip firewall nat add \
      comment="Ingress - Port 80 to Raspberry Pi ($iface) [MHS]" \
      chain=dstnat \
      in-interface=ether1 \
      protocol=tcp \
      dst-port=80 \
      action=dst-nat \
      to-addresses=$addr \
      to-ports=80
    
    # Hairpin NAT for internal LAN access
    /ip firewall nat add \
      comment="Hairpin - Ingress ($iface) [MHS]" \
      chain=srcnat \
      src-address=192.168.1.0/24 \
      protocol=tcp \
      dst-port=80 \
      dst-address=$addr \
      action=src-nat \
      to-addresses=192.168.1.1
  }
  
  :put "Port forwarding configured for both ethernet and wireless"
  /ip firewall nat print where comment~"[MHS]"
}
```

## VPN

TODO
