# Netgear R7000p

Wireless `access-point`.

Connected to [[devices/mikrotek-hex/README]]  on `ether2`.

After a factory settings reset, must be switched from router to AP mode (disabling DHCP).

## Tabs

### [Basic Setup](http://192.168.1.2/index.asp)

```yaml
WAN Setup:
  WAN Connection Type:
    Connection Type: Disabled
  Optional Settings:
    Router Name: R700P
Network Setup:
  Router IP:
    Local IP Address: 192.168.1.2/24
    Gateway: 192.168.1.1
    Local DNS: 192.168.1.1
  Dynamic Host Configuration Protocol (DHCP):
    DHCP Type: DHCP Forwarder
    DHCP Server: 192.168.1.1
  NTP Client Settings:
    Time Zone: America/New_York
```

### [Wireless Basic Settings](http://192.168.1.2/Wireless_Basic.asp)

```yaml
Wireless Interface wl0 [2.4 GHz TurboQAM] - Max Vaps(16):
  Radio Mode: AP
  Service Set Identifier (SSID): Skynet
  Channel: Auto
Wireless Interface wl1 [5 GHz/802.11ac] - Max Vaps(8):
  Radio Mode: AP
  Service Set Identifier (SSID): Skynet
  Channel: Auto
```

### [Wireless Security](http://192.168.1.2/WL_WPATable.asp)

```yaml
Wireless Security wl0:
  Physical Interface wl0 SSID [Skynet] HWAddr [6C:CD:D6:2A:9E:DF]:
    Security Mode: WPA2-PSK
    WPA Algorithms: CCMP-128 (AES)
    WPA Shared Key: 8454198484
Wireless Security wl1:
  Physical Interface wl1 SSID [Skynet] HWAddr [6C:CD:D6:2A:9E:E0]:
    Security Mode: WPA2-PSK
    WPA Algorithms: CCMP-128 (AES)
    WPA Shared Key: 8454198484
```

## [Services](http://192.168.1.2/Services.asp)

```yaml
Dnsmasq Infrastructure:
  Enable dnsmasq: Enable
  Additional Options: <see static IPs below>
Secure Shell:
  SSHd: Enable
  Authorized Keys:
    ssh-rsa AAAAB3NzaC1yc2EAAAABEQAAAgEA1Pkrd0Zcqzy8FX7/9G4RPec72opIX7rTJ12Zts027ig5EmyV2WIc3VEmXTTzcdBVmMkZ37jH9trkVIK2Em3xeQ2slsp7hPPMLoH/3yRDsl+3sXRf2zpLoM3BRisEeGa3URe4cOZM+L3OrTvSo41M7nSi0Itt7x61vXtYO3nhRj/RWrhmbwZ9sKE8SaDGYQwWVIoV++22JC8GUJO5YNXvUgazS6QHOvhqVYoZagCoBo5hu5MJsPL8o8PIy8r7s7+7Zx6T5hCL7oBKtk6e8VWqpm9LHAuOJ9SpqSwb1YEz49y3rZ+0b/d3dYYo28M8epE10ML1YIjRzOippi9VWSug9VGkjvDMh0Va9w+pJT50t3HuEdkvd5E5Pu099nTAhGrrK4dAYskyd1i7E8sgPQrJK1jvon8ffMrIo1mKfNbDbwL5Z60l90dynwk40/I47OnJgZkiiCbi6IAjcE0zYOKO3sa6c7qTfI7xUxqfZtH5MGc9cILNsMUH1iLqutXmKQ3fH1y9+MOTCdvlVfjj3Y0m727mXNk2E6s4nWyK4GLMNOJbOjEVcOvRVA/Pcr7vRtEK4GEANgV7UsuS05W91/pJ7Ks6Mb5Vkj6f+ewFVcAb7XzSVy9DXDWa7f1GWUbQX53g4YQ5D+lvkF7raaFPqTVT0Fe11pKitHtHem+Qf42ol80= dstace@gmail.com
```

### Static IPs

This `dnsmasq` config is deprecated; see [[Mikrotek hEX#Static IPs]].

```bash
# Tags: noads, yesads, family
no-resolv

# usb-c adapter
#dhcp-host=00:E0:4C:65:4D:53,set:noads,192.168.1.200,usb-ethernet,infinite

dhcp-host=30:05:5C:AF:AE:C1,set:noads,192.168.1.50,brother-mfc,infinite

# Old Lenovo laptop
dhcp-host=00:1E:65:3B:C7:94,set:noads,192.168.1.55,my-home-server,infinite

### Dan
# ethernet
dhcp-host=84:A9:38:0E:9C:2F,set:noads,192.168.1.13,dan-laptop,infinite
# wifi
dhcp-host=A8-3B-76-86-F5-D1,set:noads,192.168.1.11,dan-pc,infinite
dhcp-host=B4:B5:B6:7D:0D:D9,set:noads,192.168.1.14,dan-laptop,infinite
#dhcp-host=C6:95:C9:3F:4B:2C,set:noads,192.168.1.17,dan-phone,infinite
#dhcp-host=AE:28:A4:FE:E6:20,set:noads,192.168.1.18,dan-phone,infinite
dhcp-host=82:D2:FB:C2:12:5C,set:noads,192.168.1.19,dan-iphone,infinite
# usb-c adapter
dhcp-host=00:E0:4C:68:4B:C4,set:noads,192.168.1.15,acuity-laptop,infinite
#dhcp-host=6C:7E:67:C4:F2:B0,set:noads,192.168.1.16,dan-work-mac,infinite

### Nicole
dhcp-host=84:25:19:33:EE:80,set:noads,192.168.1.20,printer,infinite
# wifi
dhcp-host=34:F6:4B:ED:B5:7A,set:yesads,192.168.1.23,nicole-pc,infinite
# wifi
dhcp-host=04:ED:33:D1:EF:F2,set:yesads,192.168.1.25,nicole-laptop,infinite

### HTPC
# ethernet
dhcp-host=48:AD:9A:9D:24:9D,set:family,192.168.1.31,htpc-wifi,infinite

### Julian
dhcp-host=F4:AB:5C:9B:AF:8E,set:noads,192.168.1.44,julian-deck,infinite

### DNS
# Default global server used if no rules apply
server=1.1.1.1
# https://adguard-dns.io/en/public-dns.html
dhcp-option-force=tag:noads,option:dns-server,94.140.14.14,94.140.15.15
dhcp-option-force=tag:yesads,option:dns-server,94.140.14.140,94.140.14.141
dhcp-option-force=tag:family,option:dns-server,94.140.14.15,94.140.15.16
```
