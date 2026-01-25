# Checks for required variables
print_status "Validating .env configuration..."

local required_vars=(
  "DB_PASSWORD"
  "DB_USERNAME"
  "DB_DATABASE_NAME"
  "UPLOAD_LOCATION"
  "DB_DATA_LOCATION"
)

local missing_vars=()
for var in "${required_vars[@]}"; do
  if [[ -z "${!var}" ]]; then
    missing_vars+=("$var")
  fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
  print_warning "Missing environment variables in .env:"
  for var in "${missing_vars[@]}"; do
    echo "  - $var"
  done
  print_error "Please edit $SERVICE_DIR/.env and set all required variables"
  exit 1
fi

print_success ".env validation passed"
