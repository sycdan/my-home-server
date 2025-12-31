# Exports: VALID_DOMAINS (array)

parse_and_validate_domains() {
  local fleet_file="${1:-~/my-home-server/fleet.json}"
  fleet_file="$(eval echo "$fleet_file")" # expand ~
  if [[ ! -f "$fleet_file" ]]; then
    print_error "Fleet file not found: $fleet_file"
    exit 1
  fi
  # Parse domain keys from .domains object
  local -a domains
  domains=( $(jq -r '.domains | keys[]' "$fleet_file") )
  if [[ ${#domains[@]} -eq 0 ]]; then
    print_error "No domains found in $fleet_file"
    exit 1
  fi
  # Validate domains
  declare -ga VALID_DOMAINS
  VALID_DOMAINS=()
  for domain in "${domains[@]}"; do
    echo ""
    print_status "Checking domain: $domain"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://$domain" 2>/dev/null || echo "000")
    if ! [[ "$HTTP_STATUS" =~ ^[23] ]]; then
      print_warning "Domain $domain not registered (HTTP $HTTP_STATUS), skipping all services for this domain"
      continue
    fi
    print_success "Domain $domain is registered"
    VALID_DOMAINS+=("$domain")
  done
}

echo ""
parse_and_validate_domains "$1"