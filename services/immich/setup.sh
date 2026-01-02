#!/bin/bash

# Immich Service Setup Script
# This script sets up all prerequisites for running Immich
# Should be idempotent - safe to run multiple times

set -e

# Get script directory (where this script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_DIR="$SCRIPT_DIR"

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

check_root() {
	if [[ $EUID -eq 0 ]]; then
		print_error "This script should not be run as root"
		exit 1
	fi
}

check_docker() {
	if ! command -v docker &> /dev/null; then
		print_error "Docker is not installed. Please run the main setup script first."
		exit 1
	fi
	print_success "Docker is installed"
}

check_docker_compose() {
	if ! docker compose version &> /dev/null; then
		print_error "Docker Compose is not installed. Please run the main setup script first."
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
	print_status "Immich Service Setup"
	echo ""
	
	check_root
	check_docker
	check_docker_compose
	
	# Create directories first
	create_directories
	
	# Setup .env file
	create_env_file
	
	# Validate configuration
	validate_env
	
	echo ""
	print_success "Immich service is ready!"
	print_status "To start Immich, run:"
	echo "  cd $SERVICE_DIR"
	echo "  docker compose up -d"
	echo ""
	print_status "To stop Immich, run:"
	echo "  cd $SERVICE_DIR"
	echo "  docker compose down"
}

main "$@"
	
	# Get latest version
	DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
	
	# Download and install
	sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
	sudo chmod +x /usr/local/bin/docker-compose
	
	print_success "Docker Compose installed successfully"
}

configure_firewall() {
	if is_wsl; then
		print_warning "Running in WSL - skipping UFW firewall (use Windows Firewall instead)"
		return
	fi
	
	print_status "Configuring UFW firewall..."
	
	# Enable UFW
	sudo ufw --force enable
	
	# Allow SSH (important!)
	sudo ufw allow ssh
	
	# Allow Immich port
	sudo ufw allow 2283/tcp
	
	# Allow HTTP and HTTPS (for reverse proxy)
	sudo ufw allow 80/tcp
	sudo ufw allow 443/tcp
	
	print_success "Firewall configured"
	sudo ufw status
}

configure_fail2ban() {
	if is_wsl; then
		print_warning "Running in WSL - skipping fail2ban (systemd may not be available)"
		return
	fi
	
	print_status "Configuring fail2ban..."
	
	sudo systemctl enable fail2ban
	sudo systemctl start fail2ban
	
	print_success "fail2ban configured and started"
}

setup_immich_directories() {
	print_status "Setting up Immich directories..."
	
	# Create main directory
	mkdir -p ~/immich-server
	cd ~/immich-server
	
	# Create upload directory
	mkdir -p ./library
	
	# Set proper permissions
	chmod 755 ./library
	
	print_success "Immich directories created"
}

configure_immich() {
	print_status "Configuring Immich environment..."
	
	cd ~/immich-server
	
	# Generate random password for database
	DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
	
	# Update .env file with generated password
	sed -i "s/DB_PASSWORD=postgres/DB_PASSWORD=${DB_PASSWORD}/" .env
	
	# Set upload location
	sed -i "s|UPLOAD_LOCATION=./library|UPLOAD_LOCATION=$(pwd)/library|" .env
	
	print_success "Immich environment configured"
	print_status "Database password generated and configured"
}

create_systemd_service() {
	print_status "Creating systemd service for Immich..."
	
	sudo tee /etc/systemd/system/immich.service > /dev/null <<EOF
[Unit]
Description=Immich Media Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$HOME/immich-server
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF
	
	sudo systemctl daemon-reload
	sudo systemctl enable immich
	
	print_success "Systemd service created and enabled"
}

start_immich() {
	print_status "Starting Immich..."
	
	cd ~/immich-server
	docker-compose up -d
	
	print_success "Immich started successfully"
}

do_checks() {
	print_status "Performing system checks..."
	check_root
	check_ubuntu
	print_success "System checks passed"
}

do_updates() {
	print_status "Updating system..."
	sudo apt update
	sudo apt upgrade -y
	sudo apt full-upgrade -y
	sudo apt autoremove -y
	print_success "System updated"
}

install_utilities() {
	print_status "Installing utilities..."
	sudo apt install -y \
		curl \
		wget \
		git \
		nano \
		htop \
		ufw \
		fail2ban \
		unzip \
		tree
	print_success "Utilities installed"
}

do_immich() {
	print_status "Settings up Immich..."
	
	setup_immich_directories
	configure_immich
	# create_systemd_service
	start_immich
	
	display_final_info
}

display_final_info() {
	local wsl_ip
	if is_wsl; then
		wsl_ip=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
	else
		wsl_ip=$(hostname -I | awk '{print $1}')
	fi
	
	echo
	echo "=========================================="
	echo "  🎉 Immich Setup Complete!"
	echo "=========================================="
	echo
	print_success "Immich is running on: http://${wsl_ip}:2283"
	echo
	echo "📁 Immich directory: ~/immich-server"
	echo "📸 Upload directory: ~/immich-server/library"
	echo
	echo "🔧 Management commands:"
	echo "  • Start: docker-compose up -d"
	echo "  • Stop: docker-compose down"
	echo "  • Logs: docker-compose logs -f"
	echo "  • Update: docker-compose pull && docker-compose up -d"
	echo
	if ! is_wsl; then
		echo "🔥 Firewall ports opened:"
		echo "  • SSH (22)"
		echo "  • Immich (2283)"
		echo "  • HTTP (80) and HTTPS (443) for reverse proxy"
		echo
	fi
	echo "📖 Next steps:"
	echo "  1. Open http://${wsl_ip}:2283 in your browser"
	echo "  2. Create your admin account"
	echo "  3. Configure mobile apps with server URL"
	echo "  4. Consider setting up a reverse proxy with SSL (Nginx/Caddy)"
	echo
	print_warning "Remember to backup your ~/immich-server directory regularly!"
}

main() {
	echo "=========================================="
	echo "🏠 Home Server Setup Script"
	echo "=========================================="
	echo
	do_checks
	do_updates
	install_utilities
	install_docker
	install_docker_compose
	configure_firewall
	configure_fail2ban
	do_immich
}

main "$@"