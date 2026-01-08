if [[ -z "$PORKBUN_API_KEY" || -z "$PORKBUN_SECRET_KEY" ]]; then
    print_error "Missing Porkbun API credentials in .env file"
    exit 1
fi

if [[ ! "$PORKBUN_API_KEY" =~ ^pk1_ ]]; then
    print_error "PORKBUN_API_KEY must start with 'pk1_' (got: ${PORKBUN_API_KEY:0:10}...)"
    exit 1
fi

if [[ ! "$PORKBUN_SECRET_KEY" =~ ^sk1_ ]]; then
    print_error "PORKBUN_SECRET_KEY must start with 'sk1_' (got: ${PORKBUN_SECRET_KEY:0:10}...)"
    exit 1
fi

echo ""
print_success "Porkbun API credentials validated"
