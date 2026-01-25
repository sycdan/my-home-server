# HTPC

Running Windows 11 and WSL2 configured with the Ubuntu distribution.

**Note:** WSL runs per-user in Windows, so use the same (admin) user for everything.

## Add your SSH key to WSL

```pwsh
wsl.exe -d Ubuntu -- nano ~/.ssh/authorized_keys
# paste in pubkey
```

## SSH Config (WSL OpenSSH)

- SSH server runs inside WSL, not Windows
- You connect directly to your Linux environment
- Windows never exposes a shell over SSH

**Note:** Open a terminal inside your WSL distro to run these commands, e.g. Start -> Ubuntu.

### Install OpenSSH Server inside WSL

Install ssh:

```bash
sudo apt update
sudo apt install openssh-server -y
```

Run on startup:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Set SSH Server to Listen on Port 22

By default, WSL listens on its own internal IP.

We want it to listen on all interfaces so Windows can forward to it.

```bash
sudo nano /etc/ssh/sshd_config
```

Ensure these lines exist and are not commented out:

```text
Port 22
AddressFamily inet
ListenAddress 0.0.0.0

PubkeyAuthentication yes

PasswordAuthentication no
```

Save, then restart SSH and ensure it's listening on 0.0.0.0 port 22:

```bash
sudo systemctl restart ssh
sudo systemctl status ssh | grep listening
```

### Forward Windows Port 22 to WSL Port 22

Windows needs to forward incoming SSH traffic to WSL.

To do this, it needs a firewall rule to forward to the WSL IP.

Problem is, the WSL IP changes, so create a PowerShell script in `notepad`:

```pwsh
Set-Content -Path "C:\wsl-up.ps1" -Value @'
Write-Output "Shutting down WSL..."
wsl.exe --shutdown

Write-Output "Starting WSL..."
wsl.exe -d Ubuntu -- true

Write-Output "Giving WSL a moment to fully initialize networking..."
Start-Sleep -Seconds 2

Write-Output "Getting the current WSL IP address..."
$ip = (wsl.exe -d Ubuntu -- hostname -I).Trim().Split()[0]

if (-not $ip) {
  Write-Output "ERROR: Could not determine WSL IP address."
  exit 1
}

Write-Output "WSL IP detected: $ip"

Write-Output "Resetting existing portproxy rules..."
netsh interface portproxy reset

Write-Output "Adding new portproxy rule for SSH..."
netsh interface portproxy add v4tov4 `
  listenport=22 listenaddress=0.0.0.0 `
  connectport=22 connectaddress=$ip

Write-Output "Portproxy rule updated to forward port 22 to $ip"

Write-Output "AH AH AH AH STAYING ALIIIIVE!"
wsl.exe -d Ubuntu -- nohup sleep infinity
'@
# Ensure content was written
Get-Content "C:\wsl-up.ps1"
# Run manually to test:
powershell.exe -ExecutionPolicy Bypass -File "C:\wsl-up.ps1"
```

Start -> Scheduled Tasks -> Run as Administrator:

```yaml
name: Run WSL on startup
trigger: When the computer starts
action: Start a program
program: powershell.exe
arguments: -ExecutionPolicy Bypass -File "C:\wsl-up.ps1"
security: |
  Run as <Admin Name>
  Run whether user is logged in or not
  Run with highest privileges
```

Show rules:

```pwsh
netsh interface portproxy show v4tov4
```

Clear all rules:

```pwsh
netsh interface portproxy reset
```

## Disable Windows SSH

```pwsh
Stop-Service sshd
Set-Service sshd -StartupType Disabled
```

## Unblock Window SSH port

```pwsh
New-NetFirewallRule -DisplayName "WSL SSH" -Direction Inbound -LocalPort 22 -Protocol TCP -Action Allow
```

## Troubleshooting

### WSL hangs

```cmd
taskkill /f /im /wsl.exe
powershell
```

```pwsh
Get-Service | Where-Object {$_.Name -like "*wsl*" -or $_.DisplayName -like "*wsl*"}
Restart-service WSLService
```
