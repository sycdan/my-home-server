# External Storage Setup

This guide documents setting up external drives (USB, external USB drives like MyPassport) for persistent service data.

## WD MyPassport Configuration

**Hardware:** WD MyPassport (USB external drive, NTFS formatted)  
**UUID:** `448A4A818A4A700A`  
**Device:** `/dev/sdb1`  
**Mount Point:** `/mnt/mypassport`  
**Setup Date:** 2026-01-05

### Automount on Startup

The drive is configured in `/etc/fstab` with the `nofail` option, which means:

1. **If the drive IS connected:** It mounts automatically at `/mnt/mypassport` on startup
2. **If the drive is NOT connected:** The system continues booting without error (nofail flag prevents boot failure)

**fstab entry:**
```bash
UUID=448A4A818A4A700A /mnt/mypassport ntfs uid=1000,gid=1000,umask=0002,nofail 0 0
```

### Symlinked Data

The following service data is stored on MyPassport:

#### Immich Photo Library

- **Location:** `/mnt/mypassport/immich-library`
- **Symlink:** `/home/dan/my-home-server/services/immich/library → /mnt/mypassport/immich-library`
- **What happens if drive is disconnected at startup:**
  - Boot continues normally (nofail flag)
  - Immich service will start, but the `library` symlink will be broken
  - The service will fail when trying to access photo/video files
  - Once the drive is connected, the symlink becomes valid again (no restart needed)

### Manual Mount/Unmount

If you need to manually unmount or remount:

```bash
# Unmount
sudo umount /mnt/mypassport

# Remount
sudo mount /mnt/mypassport

# Verify
df -h | grep mypassport
```

### Permissions

Ownership and permissions are set for user `dan` and group `docker`:

```bash
sudo chown -R dan:docker /mnt/mypassport/immich-library
```

This allows:
- Direct filesystem access by the user
- Docker containers running as root to access the data

### Troubleshooting

**"Device not found" on startup:**
- Likely cause: drive UUID changed or different USB port
- Fix: Run `sudo blkid` and update UUID in `/etc/fstab` if needed

**Symlink broken after reconnection:**
- The symlink is always valid; if the mount was lost, reconnect the drive
- Services may need a restart if they cached "path not found" errors:
  ```bash
  ./ctl immich down && ./ctl immich up
  ```

**Permission denied errors:**
- Check ownership: `ls -lh /mnt/mypassport/immich-library`
- Fix with: `sudo chown -R dan:docker /mnt/mypassport/immich-library`

### Backup Strategy

Because this drive holds your photo library, consider:
- Keeping a backup copy on the main system or another external drive
- Monitoring drive health regularly
- Testing backups periodically
