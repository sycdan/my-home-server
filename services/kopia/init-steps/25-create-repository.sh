
# Check if repository exists, create it if not
if ! ./bin/kopia repository status >/dev/null 2>&1; then
  print_status "Creating new repository..."
  ./bin/kopia repository create filesystem --path=/repository
else
  repo_status=$(./bin/kopia repository status --json)
  config_file=$(echo "$repo_status" | jq -r '.configFile')
  print_success "Repository config: $config_file"
fi

