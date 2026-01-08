# Exports: VALID_DOMAINS (array)

parse_and_validate_domains() {
  local domains_filepath="${1:-~/my-home-server/domains.json}"
  domains_filepath="$(eval echo "$domains_filepath")" # expand ~
  if [[ ! -f "$domains_filepath" ]]; then
    print_error "Domains config file not found: $domains_filepath"
    exit 1
  fi
  echo "Using domains config file: $domains_filepath"
  # Parse domains.json into CONFIG_DOMAINS associative array (local only)
  local -A config_domains
  while IFS= read -r domain; do
    config_domains["$domain"]=1
  done < <(jq -r 'keys[]' "$domains_filepath")
  # Validate domains
  declare -ga VALID_DOMAINS
  VALID_DOMAINS=()
  for domain in "${!config_domains[@]}"; do
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