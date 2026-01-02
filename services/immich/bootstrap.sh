# This script sets up the Immich service configuration
# Should be idempotent - safe to run multiple times

set -e

# Find the directory where this script is located
SERVICE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
	echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
	echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

print_error() {
	echo -e "${RED}[ERROR]${NC} $1" >&2
}

check_docker() {
	if ! command -v docker &> /dev/null; then
		print_error "Docker is not installed. Please run the main init script first."
		exit 1
	fi
	print_success "Docker is installed"
}

check_docker_compose() {
	if ! docker compose version &> /dev/null; then
		print_error "Docker Compose is not installed. Please run the main init script first."
		exit 1
	fi
	print_success "Docker Compose is available"
}

create_env_file() {
	if [[ -f "$SERVICE_DIR/.env" ]]; then
		print_status ".env file already exists, skipping creation"
		return
	fi
	
	if [[ ! -f "$SERVICE_DIR/example.env" ]]; then
		print_error "example.env not found in $SERVICE_DIR"
		exit 1
	fi
	
	print_status "Creating .env file from example.env..."
	cp "$SERVICE_DIR/example.env" "$SERVICE_DIR/.env"
	print_success ".env file created"
	print_warning "IMPORTANT: Edit $SERVICE_DIR/.env with your configuration values"
}

create_directories() {
	print_status "Creating required directories..."
	
	# Read directories from .env or use defaults
	UPLOAD_LOCATION="${UPLOAD_LOCATION:-.immich/data}"
	DB_DATA_LOCATION="${DB_DATA_LOCATION:-.immich/db}"
	
	# Create directories if they don't exist
	mkdir -p "$UPLOAD_LOCATION"
	mkdir -p "$DB_DATA_LOCATION"
	
	print_success "Directories created/verified"
}

validate_env() {
	print_status "Validating .env configuration..."
	
	if [[ ! -f "$SERVICE_DIR/.env" ]]; then
		print_error ".env file not found"
		exit 1
	fi
	
	# Source the .env file
	set +e
	source "$SERVICE_DIR/.env" 2>/dev/null
	set -e
	
	# Check for required variables
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
}

main() {
	print_status "Immich Service Bootstrap"
	echo ""
	
	check_docker
	check_docker_compose
	
	create_directories
	create_env_file
	validate_env
	
	echo ""
	print_success "Immich service is ready!"
	print_status "To start Immich, run:"
	echo "  bash ctl.sh up immich"
	echo ""
	print_status "To stop Immich, run:"
	echo "  bash ctl.sh down immich"
	echo ""
	print_status "View logs with:"
	echo "  bash ctl.sh logs immich"
}

main "$@"
