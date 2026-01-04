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

/ip dhcp-server lease print
