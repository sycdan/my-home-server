if [[ -z "$MHS_FLEET_FILEPATH" ]]; then
  print_error "MHS_FLEET_FILEPATH not set"
  exit 1
else
  echo "Using fleet file path: $MHS_FLEET_FILEPATH"
fi

if [[ -z "$MHS_CNAME_TARGET" ]]; then
  print_error "MHS_CNAME_TARGET not set"
  exit 1
else
  echo "Using CNAME target: $MHS_CNAME_TARGET"
fi
