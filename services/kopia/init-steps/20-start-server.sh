cd "$SERVICE_DIR"

docker compose up -d
# alias kopia="docker exec -it -e KOPIA_PASSWORD=\"${KOPIA_PASSWORD}\" kopia kopia"
# kopia server acl add --user admin@whh --access FULL --target type=user
