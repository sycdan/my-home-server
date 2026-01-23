cd "$SERVICE_DIR"

for dir in "${NUKE_DIRS[@]}"; do
  echo "Nuking directory: $dir"
  sudo rm -rf "./$dir"
done