validate_porkbun_credentials() {
  local api_key=$1
  local secret_key=$2
  
  if [[ -z "$api_key" || -z "$secret_key" ]]; then
    print_error "Missing Porkbun API credentials in .env file"
    exit 1
  fi
  
  if [[ ! "$api_key" =~ ^pk1_ ]]; then
    print_error "PORKBUN_API_KEY must start with 'pk1_' (got: ${api_key:0:10}...)"
    exit 1
  fi
  
  if [[ ! "$secret_key" =~ ^sk1_ ]]; then
    print_error "PORKBUN_SECRET_KEY must start with 'sk1_' (got: ${secret_key:0:10}...)"
    exit 1
  fi
}

echo ""
validate_porkbun_credentials "$PORKBUN_API_KEY" "$PORKBUN_SECRET_KEY"
print_success "Porkbun API credentials validated"