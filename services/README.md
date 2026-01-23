# Services

## Run a command

```bash
./run services/service/bin/script
```

### Enable sudo

Some scripts require sudo ability, which is tricky when running remotely.

Run this on the server machine, during an interactive session:

```bash
# Create the sudoers rule
echo "$(whoami) ALL=(ALL) NOPASSWD: /bin/rm, /bin/chown, /usr/bin/docker, /usr/bin/systemctl" | sudo tee /etc/sudoers.d/my-home-server-$(whoami)

# Set permissions
sudo chmod 0440 /etc/sudoers.d/my-home-server-$(whoami)

# Verify the syntax
sudo visudo -c
```
