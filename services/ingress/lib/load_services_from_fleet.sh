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
    # Skip the ingress service itself
    if [[ "$service_name" == "ingress" ]]; then
      continue
    fi
    
    # get the actual domain from the domain_key
    local domain=$(jq -r --arg dk "$domain_key" '.domains[$dk].domain' "$fleet_file")
    if [[ -z "$domain" || "$domain" == "null" ]]; then
      print_warning "Domain key '$domain_key' not found for service '$service_name' on device '$device_name', skipping"
      continue
    fi
    
    # Construct full service entry
    local service_entry="${subdomain}.${domain}|${device_name}.lan|${port}"
    SERVICES+=("$service_entry")
    echo "  Loaded service: $service_entry"
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