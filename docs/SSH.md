# Configuring SSH

Put your SSH pubkey in `~/ssh/authorized_keys`.

## Install SSH

### Ubuntu

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

## Create Key (optional)

If the device needs to be able to SSH into other devices, it needs its own key:

```bash
# Create (but don't overwrite) a new RSA key and list all public keys
ssh device 'ssh-keygen -t rsa -b 4096 -N "" -q <<< ""'
ssh device 'cat .ssh/*.pub'
```
