# Finds reachable IPs for reverse proxy and services and updates DNS entries

:local reverseProxy {
  "hostname"="ingress.lan";
  "interfaces"={
    {"B8:27:EB:AB:C0:DC"; "ethernet"};
    {"B8:27:EB:FE:95:89"; "wireless"};
  }
}

:local services {
  {
    "hostname"="immich.lan";
    "interfaces"={
      {"00:23:5A:1A:A4:F6"; "ethernet"};
      {"00:1E:65:3B:C7:94"; "wireless"};
    }
  };
  {
    "hostname"="jellyfin.lan";
    "interfaces"={
      {"A8:A1:59:F1:3E:B5"; "ethernet"};
    }
  };
}

:local findReachableIp do={
  # Try each MAC in order (earlier ones are more preferred)
  # Return the first reachable interface and its IP, or an empty string if none are reachable
  :local interfaces $1
  :foreach interface in=$interfaces do={
    :local mac ($interface->0)
    :local iftype ($interface->1)
    :put "  Trying MAC $mac ($iftype)"
    :local leaseEntries [/ip dhcp-server lease find where active-mac-address=$mac]
    :if ([:len $leaseEntries] > 0) do={
      :foreach leaseIndex in=$leaseEntries do={
        :local lease [/ip dhcp-server lease get $leaseIndex]
        :local ip ($lease->"active-address")
        :put "    Pinging $ip"
        :local pingResult [/ping $ip count=1]
        :if ($pingResult > 0) do={
          :put "    Ping succeeded"
          :return {"$ip"; "$iftype"; "$mac"}
        } else={
          :put "    Ping failed"
        }
      }
    } else={
      :put "    No active addresses"
    }
  }
  :put "  No reachable address found"
  :return ""
}

:local updateDnsEntry do={
  :local hostname $1
  :local ip $2
  :local mac $3
  :local iftype $4
  
  /ip dns static remove [find name="$hostname"]
  /ip dns static add name="$hostname" address="$ip" comment="$mac ($iftype) [MHS]"
  :put "  DNS updated: $hostname -> $ip"
}

:put "==== Updating DNS Entries ===="

# Update Reverse Proxy
:put "\nReverse Proxy:"
:local rpResult [$findReachableIp ($reverseProxy->"interfaces")]
:local rpHostname ($reverseProxy->"hostname")

:if ($rpResult != "") do={
  :local rpIp ($rpResult->0)
  :local rpIftype ($rpResult->1)
  :local rpMac ($rpResult->2)
  :put "  Using IP $rpIp (MAC: $rpMac, type: $rpIftype)"
  [$updateDnsEntry $rpHostname $rpIp $rpMac $rpIftype]
} else={
  :put "  ERROR: Could not find reachable reverse proxy IP"
}

# Update Services
:foreach service in=$services do={
  :local hostname ($service->"hostname")
  :local interfaces ($service->"interfaces")
  :put "\n$hostname"
  
  :local result [$findReachableIp $interfaces]
  
  :if ($result != "") do={
    :local ip ($result->0)
    :local iftype ($result->1)
    :local mac ($result->2)
    :put "  Using IP $ip (MAC: $mac, type: $iftype)"
    [$updateDnsEntry $hostname $ip $mac $iftype]
  } else={
    :put "  ERROR: Could not find reachable IP for $hostname"
  }
}

:put "\n==== Updating NAT Rules ===="

# Update NAT rules for the reverse proxy if its IP changed
:if ($rpResult != "") do={
  :local rpIp ($rpResult->0)
  
  # Check if HTTP dstnat rule exists and update it in place (zero downtime)
  :local httpRule [/ip firewall nat find where comment="Ingress HTTP [MHS]" chain=dstnat]
  :if ([:len $httpRule] > 0) do={
    # Rule exists, update it if IP changed
    :local ruleId ($httpRule->0)
    :local existingIp [/ip firewall nat get $ruleId to-addresses]
    :if ($existingIp != $rpIp) do={
      :put "Updating HTTP NAT rule: $existingIp -> $rpIp"
      /ip firewall nat set $ruleId to-addresses=$rpIp
    } else={
      :put "HTTP NAT rule is correct"
    }
  } else={
    # Rule doesn't exist, create it
    :put "Creating HTTP NAT rule for $rpIp"
    /ip firewall nat add comment="Ingress HTTP [MHS]" chain=dstnat in-interface=ether1 protocol=tcp dst-port=80 action=dst-nat to-addresses=$rpIp to-ports=80
  }
  
  # Check if HTTPS dstnat rule exists and update it in place
  :local httpsRule [/ip firewall nat find where comment="Ingress HTTPS [MHS]" chain=dstnat]
  :if ([:len $httpsRule] > 0) do={
    # Rule exists, update it if IP changed
    :local ruleId ($httpsRule->0)
    :local existingIp [/ip firewall nat get $ruleId to-addresses]
    :if ($existingIp != $rpIp) do={
      :put "Updating HTTPS NAT rule: $existingIp -> $rpIp"
      /ip firewall nat set $ruleId to-addresses=$rpIp
    } else={
      :put "HTTPS NAT rule is correct"
    }
  } else={
    # Rule doesn't exist, create it
    :put "Creating HTTPS NAT rule for $rpIp"
    /ip firewall nat add comment="Ingress HTTPS [MHS]" chain=dstnat in-interface=ether1 protocol=tcp dst-port=443 action=dst-nat to-addresses=$rpIp to-ports=443
  }
  
  # Hairpin NAT rules (these don't depend on reverse proxy IP, just ensure they exist)
  :local hairpinHttp [/ip firewall nat find where comment="Hairpin Ingress HTTP [MHS]"]
  :if ([:len $hairpinHttp] = 0) do={
    :put "Creating Hairpin HTTP NAT rule"
    /ip firewall nat add comment="Hairpin Ingress HTTP [MHS]" chain=srcnat src-address=192.168.1.0/24 protocol=tcp dst-port=80 action=src-nat to-addresses=192.168.1.1
  }
  
  :local hairpinHttps [/ip firewall nat find where comment="Hairpin Ingress HTTPS [MHS]"]
  :if ([:len $hairpinHttps] = 0) do={
    :put "Creating Hairpin HTTPS NAT rule"
    /ip firewall nat add comment="Hairpin Ingress HTTPS [MHS]" chain=srcnat src-address=192.168.1.0/24 protocol=tcp dst-port=443 action=src-nat to-addresses=192.168.1.1
  }
  
  :put "NAT rules are up to date"
}

:put "\n==== Updating Split DNS Entries ===="

# Update split DNS entries for external domains to point to reverse proxy
:if ($rpResult != "") do={
  :local rpIp ($rpResult->0)
  
  # List of external domains that should resolve to the reverse proxy internally
  :local externalDomains {
    "photos.sycdan.com"
    "stream.sycdan.com"
  }
  
  # Remove old split DNS entries
  /ip dns static remove [find comment~"Split DNS"]
  
  # Add new entries pointing to reverse proxy IP
  :foreach domain in=$externalDomains do={
    :put "Split DNS: $domain -> $rpIp"
    /ip dns static add name=$domain address=$rpIp comment="Split DNS"
  }
} else={
  :put "ERROR: Reverse proxy IP not found, skipping split DNS update"
}

:put "\n==== Current DNS Entries ===="
/ip dns static print where comment~"[MHS]"
