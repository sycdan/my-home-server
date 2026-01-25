# Uses paths from .env
print_status "Creating required directories..."

mkdir -p "$UPLOAD_LOCATION"
mkdir -p "$DB_DATA_LOCATION"

print_success "Directories created/verified"