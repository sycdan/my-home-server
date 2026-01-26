#!/usr/bin/env python
from argparse import ArgumentParser
from pathlib import Path

from mhs.service.immich.restore_backup.command import RestoreBackup


def main(argv=None):
  parser = ArgumentParser(description="Restore an Immich backup.")
  parser.add_argument(
    "--database-backup-file",
    type=Path,
    help="Path to the database backup file (e.g. library/backups/immich-db-backup*)",
  )
  args = parser.parse_args(argv)

  RestoreBackup(database_backup_file=args.database_backup_file).execute()


if __name__ == "__main__":
  main()
