# Exports: SERVICES (array), CNAME_TARGET (string)

load_services_from_fleet() {
  local fleet_file="${FLEET_FILEPATH:-~/my-home-server/fleet.json}"
  fleet_file="$(eval echo "$fleet_file")" # expand ~
  if [[ ! -f "$fleet_file" ]]; then
    print_error "Fleet file not found: $fleet_file"
    exit 1
  fi
  
  echo "Loading services from: $fleet_file"
  
  # Get CNAME_TARGET from environment or use default
  CNAME_TARGET="${MHS_CNAME_TARGET:-home.sycdan.com}"
  
  # Load services from fleet file
  declare -ga SERVICES
  SERVICES=()
  
  # Parse services from devices with simpler approach
  local temp_file=$(mktemp)
  jq -r '.devices | to_entries[] | select(.value.services != null) | .key as $device | .value.services | to_entries[] | "\($device)|\(.key)|\(.value.port)"' "$fleet_file" > "$temp_file"
  
  while IFS='|' read -r device_name service_name port; do
    if [[ -n "$device_name" && -n "$service_name" && -n "$port" ]]; then
      # Map service names to external subdomains and domains
      case "$service_name" in
        "immich")
          external_hostname="photos.wildharvesthomestead.com"
          ;;
        "jellyfin")
          external_hostname="stream.wildharvesthomestead.com"
          ;;
        *)
          print_warning "Unknown service '$service_name' on device '$device_name', skipping"
          continue
          ;;
      esac
      
      # Create service entry: "external_hostname|device.lan|port"
      service_entry="${external_hostname}|${device_name}.lan|${port}"
      SERVICES+=("$service_entry")
      echo "  Loaded service: $service_entry"
    fi
  done < "$temp_file"
  
  rm -f "$temp_file"
}

echo ""
load_services_from_fleet "$MHS_FLEET_FILEPATH"
if [[ ${#SERVICES[@]} -eq 0 ]]; then
  print_warning "No services found in $fleet_file"
else
  echo "Loaded ${#SERVICES[@]} services from fleet file"
fi