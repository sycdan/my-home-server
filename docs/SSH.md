# Configuring SSH

Put your SSH pubkey in `~/ssh/authorized_keys`.

## Ubuntu

```bash
# update system
sudo apt update
sudo apt upgrade -y

# install openssh server
sudo apt install ssh -y

# start server on boot
sudo systemctl enable ssh

# verify status
sudo systemctl status ssh

# allow ssh through firewall
sudo ufw allow ssh
sudo ufw enable
```
