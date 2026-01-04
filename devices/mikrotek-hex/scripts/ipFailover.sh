# Ensure all static IPs are bound to reachable interfaces
# First interface is preferred; second is fallback
:local devices {
  {
    "name"="Raspberry Pi 3";
    "targetIp"="192.168.1.3";
    "interfaces"={
      {"B8:27:EB:AB:C0:DC"; "ethernet"};
      {"B8:27:EB:FE:95:89"; "wireless"};
    }
  };
  {
    "name"="HTPC";
    "targetIp"="192.168.1.10";
    "interfaces"={
      {"A8:A1:59:F1:3E:B5"; "ethernet"};
    }
  };
  {
    "name"="Old Lenovo Laptop";
    "targetIp"="192.168.1.11";
    "interfaces"={
      {"00:23:5A:1A:A4:F6"; "ethernet"};
      {"00:1E:65:3B:C7:94"; "wireless"};
    }
  };
  {
    "name"="Dan's PC";
    "targetIp"="192.168.1.13";
    "interfaces"={
      {"9C:6B:00:3F:C3:CA"; "ethernet"};
    }
  };
  {
    "name"="Dan's Laptop";
    "targetIp"="192.168.1.14";
    "interfaces"={
      {"84:A9:38:0E:9C:2F"; "ethernet"};
      {"B4:B5:B6:7D:0D:D9"; "wireless"};
    }
  };
}

:local selectBestInterface do={
  :local interfaceList $1
  :local bestInterface ""
  :local bestTime 0
  
  # If there's a reachable MAC, just use that
  :foreach interface in=$interfaceList do={
    :local mac ($interface->0)
    :local type ($interface->1)
    :local arpEntries [/ip arp find where mac-address=$mac and status="reachable"]
    
    :if ([:len $arpEntries] > 0) do={
      :put "  MAC $mac ($type) is reachable"
      :return $interface
    }
  }
  
  # Helper to convert time string to seconds
  :local timeToSec do={
    :local str $1
    :if ($str = "never") do={:return 999999999}
    :local sec 0
    :local dPos [:find $str "d"]
    :if ($dPos >= 0) do={:set sec ($sec + [:tonum [:pick $str 0 $dPos]] * 86400); :set str [:pick $str ($dPos + 1) 999]}
    :local hPos [:find $str "h"]
    :if ($hPos >= 0) do={:set sec ($sec + [:tonum [:pick $str 0 $hPos]] * 3600); :set str [:pick $str ($hPos + 1) 999]}
    :local mPos [:find $str "m"]
    :if ($mPos >= 0) do={:set sec ($sec + [:tonum [:pick $str 0 $mPos]] * 60); :set str [:pick $str ($mPos + 1) 999]}
    :local sPos [:find $str "s"]
    :if ($sPos >= 0) do={:set sec ($sec + [:tonum [:pick $str 0 $sPos]])}
    :return $sec
  }

  # If no reachable MAC, find the one with the most recent DHCP lease activity
  :foreach interface in=$interfaceList do={
    :local mac ($interface->0)
    :local type ($interface->1)
    :local leaseEntries [/ip dhcp-server lease find where mac-address=$mac]
    
    :if ([:len $leaseEntries] > 0) do={
      :local lease [/ip dhcp-server lease get ($leaseEntries->0)]
      :local lastSeenStr ($lease->"last-seen")
      :local lastSeen [$timeToSec $lastSeenStr]
      :put "  MAC $mac ($type) was last seen $lastSeen seconds ago ($lastSeenStr)"
      
      :if ($lastSeen > $bestTime) do={
        :set bestTime $lastSeen
        :set bestInterface $interface
      } else={
        :put "  MAC $mac ($type) has no lease"
      }
    }
  }
  
  # Fallback to first interface in list
  :if ($bestInterface = "") do={
    :set bestInterface ($interfaceList->0)
  }
  
  :return $bestInterface
}

# Process each device and update DHCP lease
:put "==== Refreshing Static IP Bindings ===="
:foreach device in=$devices do={
  :local deviceName ($device->"name")
  :local targetIp ($device->"targetIp")
  :local interfaces ($device->"interfaces")
  :put "\n$deviceName ($targetIp)"
  
  :local bestInterface [$selectBestInterface $interfaces]
  :local bestMac ($bestInterface->0)
  :local bestType ($bestInterface->1)
  
  :put "  Using MAC $bestMac ($bestType)"
  
  # Check if lease exists
  :local leaseEntry [/ip dhcp-server lease find where address=$targetIp]
  :if (($leaseEntry != "") && ($leaseEntry != 0)) do={
    # Get current lease details
    :local currentLease [/ip dhcp-server lease get $leaseEntry]
    :local currentMac ($currentLease->"mac-address")
    
    :if ($currentMac != $bestMac) do={
      :put "  Updating lease MAC: $currentMac -> $bestMac"
      /ip dhcp-server lease set $leaseEntry mac-address="$bestMac"
    } else={
      :put "  Lease MAC already correct"
    }
  } else={
    :put "  Creating new DHCP lease for $bestMac"
    /ip dhcp-server lease add address="$targetIp" mac-address="$bestMac" comment="$deviceName"
  }
  
  # Remove any other leases for this MAC (for different IPs)
  :local allMacLeases [/ip dhcp-server lease find where mac-address=$bestMac]
  :foreach macLease in=$allMacLeases do={
    :local lease [/ip dhcp-server lease get $macLease]
    :local leaseIp ($lease->"address")
    :if ($leaseIp != $targetIp) do={
      :put "  Removing stale lease: $bestMac -> $leaseIp"
      /ip dhcp-server lease remove $macLease
    }
  }
}

:put "\n==== Current DHCP Leases ===="
/ip dhcp-server lease print
