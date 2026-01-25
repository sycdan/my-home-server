# set -x
cd "$SERVICE_DIR"

if [[ -z "$BACKUP_PATH" ]]; then
  print_status "No --from-backup option provided, skipping"
  return
fi

backup_path="$(realpath "$BACKUP_PATH")"
if [[ -f "$backup_path" ]]; then
  print_status "Restoring Immich DB from: $backup_path"
else
  print_error "Backup file not found: $BACKUP_PATH"
  exit 1
fi

docker compose down -v          # Stop Immich apps and remove volumes
rm -rf $DB_DATA_LOCATION        # CAUTION! Deletes all Immich data (except uploads) to start from scratch
docker compose pull             # Update to latest version of Immich (optional)
docker compose create           # Create Docker containers for Immich apps without running them
docker start immich_postgres    # Start Postgres server
sleep 10                        # Wait for Postgres server to start up
# Check the database user if you deviated from the default
gunzip --stdout $backup_path \
| sed "s/SELECT pg_catalog.set_config('search_path', '', false);/SELECT pg_catalog.set_config('search_path', 'public, pg_catalog', true);/g" \
| docker exec -i immich_postgres psql --dbname=postgres --username="$DB_USERNAME"  # Restore Backup
docker compose up -d            # Start remainder of Immich apps

print_success "Immich DB restoration complete!"
print_warning "You need to manually move your files into the UPLOAD_LOCATION: $UPLOAD_LOCATION"