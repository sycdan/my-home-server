# HTPC

Running Windows 11 and Docker Dsktop, with WSL2/Ubuntu engine.

## Trouble shooting

If you get this when pulling:

```text
error getting credentials - err: exit status 1, out: `A specified logon session does not exist. It may already have been terminated.`
```

Change `~/.docker/config.json`:

```json
{
  "auths": {},
  "credsStore": "ecr-login"
}
```
