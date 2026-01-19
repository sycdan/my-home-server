# Exports: SERVICES (array)

load_services_from_fleet() {
  local fleet_file=$1
  local cname_target=$2
  
  fleet_file="$(eval echo "$fleet_file")" # expand ~
  if [[ ! -f "$fleet_file" ]]; then
    print_error "Fleet file not found: $fleet_file"
    exit 1
  fi
  
  echo "Loading services from: $fleet_file"
  declare -ga SERVICES
  SERVICES=()
  local temp_file=$(mktemp)
  jq -r '.devices | to_entries[] | select(.value.services != null) | .key as $device | .value.services | to_entries[] | "\($device)|\(.key)|\(.value.port)|\(.value.subdomain)|\(.value.domain_key)"' "$fleet_file" > "$temp_file"
  
  while IFS='|' read -r device_name service_name port subdomain domain_key; do
    if [[ -n "$device_name" && -n "$service_name" && -n "$port" && -n "$subdomain" && -n "$domain_key" ]]; then
      # get the actual domain from domain_key
      local domain=$(jq -r --arg dk "$domain_key" '.domains[$dk].domain' "$fleet_file")
      if [[ -z "$domain" || "$domain" == "null" ]]; then
        print_warning "Domain key '$domain_key' not found for service '$service_name' on device '$device_name', skipping"
        continue
      fi
      
      # Construct full service entry
      local full_hostname="${subdomain}.${domain}"
      service_entry="${full_hostname}|${device_name}.lan|${port}"
      SERVICES+=("$service_entry")
      echo "  Loaded service: $service_entry"
    else
      print_warning "Incomplete service definition in fleet file for device '$device_name', skipping"
    fi
  done < "$temp_file"
  
  rm -f "$temp_file"
}

echo ""
load_services_from_fleet "$MHS_FLEET_FILEPATH"
if [[ ${#SERVICES[@]} -eq 0 ]]; then
  print_warning "No services found in fleet file"
else
  echo "Loaded ${#SERVICES[@]} services from fleet file"
fi