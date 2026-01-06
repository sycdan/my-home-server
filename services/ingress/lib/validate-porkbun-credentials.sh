# Check for .env file and create from example if needed
if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    print_status "Creating .env file from example..."
    cp "$SCRIPT_DIR/example.env" "$SCRIPT_DIR/.env"
    print_warning ".env file created. Please edit it with your Porkbun API credentials:"
    print_warning "  $SCRIPT_DIR/.env"
    read -p "Press enter once you've added your API key and secret: "
fi

# Source .env and validate credentials
source "$SCRIPT_DIR/.env"

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

print_success "Porkbun API credentials validated"
