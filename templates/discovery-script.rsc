:local hostname "{{hostname}}"
:local primaryMac "{{primary_mac}}"
:local secondaryMac "{{secondary_mac}}"

# Returns a list of known IPs for a given MAC
:local getIpsForMac do={
  :local mac $1
  # Making an empty array errors, so start with one empty element
  :local ips {""}
  # DHCP leases
  :foreach leaseIndex in=[/ip dhcp-server lease find where active-mac-address=$mac] do={
    :local ip [/ip dhcp-server lease get $leaseIndex value-name=active-address]
    :if ($ip != "") do={
      :set ips ($ips, $ip)
    }
  }
  # ARP table
  :foreach arpIndex in=[/ip arp find where mac-address=$mac] do={
    :local ip [/ip arp get $arpIndex value-name=address]
    :if ($ip != "") do={
      :set ips ($ips, $ip)
    }
  }
  # Remove the first empty element and return the rest
  :return [:pick $ips 1 [:len $ips]]
}

# Return the first reachable IP and its MAC, or empty array if none are reachable
:local findReachableIp do={
  :local ips $1
  :local mac $2
  :foreach ip in=$ips do={
    :if ([:len $ip] > 0) do={
      :put "  Pinging $ip"
      :local pingResult [/ping $ip count=1]
      :if ($pingResult > 0) do={
        :put "    Ping succeeded"
        :return {$ip; $mac}
      } else={
        :put "    Ping failed"
      }
    }
  }
  :return ""
}

:local updateDnsEntry do={
  :local hostname $1
  :local ip $2
  :local mac $3
  /ip dns static remove [find name=$hostname]
  /ip dns static add name=$hostname address=$ip comment="$mac [MHS]" ttl=5m
  :put "  DNS updated: $hostname -> $ip"
}

:put "=== Discovering $hostname ==="

:local result ""
:local macs {$primaryMac; $secondaryMac}
:foreach mac in=$macs do={
  :if ([:len $result] = 0) do={
    :if ([:len $mac] > 0) do={
      :put "Trying MAC $mac"    
      :local ips [$getIpsForMac $mac]
      :put ("  " . [:len $ips] . " IPs found")
      :if ([:len $ips] > 0) do={
        :local reachable [$findReachableIp $ips $mac]
        :if ([:len $reachable] > 0) do={
          :set result $reachable
        } else={
          :put "  No reachable IP found"
        }
      } else={
        :put "  No IPs found"
      }
    }
  }
}

:if ([:len $result] > 0) do={
  :local ip ($result->0)
  :local mac ($result->1)
  :put "Using IP $ip (MAC: $mac)"
  [$updateDnsEntry $hostname $ip $mac]
} else={
  :put "ERROR: Could not find reachable IP for $hostname"
}

:put "=== Complete ==="