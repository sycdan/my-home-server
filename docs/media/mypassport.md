# WD MyPassport — Device Record

**Device Type:** External USB drive (Silver WD MyPassport) 
**Filesystem:** NTFS  
**UUID:** `448A4A818A4A700A`  
**Status:** Currently holds an olf backup N's home files and the Immich library

## Purpose (Historical)

This drive previously stored external service data, primarily:

- **Immich photo library**  
  Located at `/mnt/mypassport/immich-library`  
  Symlinked from the Immich service directory

## System Integration (Historical)

- Mounted via `/etc/fstab` using the `nofail` option  
- Owned by user `dan` and group `docker` for container access  
- Served as persistent storage for media files

## Notes

- If reattached in the future, the UUID and mount point above should still identify it  
- Contains historical Immich media data unless wiped  
- No longer required by the current server layout but kept in records for traceability
