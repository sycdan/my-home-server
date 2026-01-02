#!/bin/bash

# Home Server Controller - Main Setup Script
# This script bootstraps Docker and sets up selected services

set -e

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

check_os() {
	if [[ ! -f /etc/os-release ]]; then
		print_error "Cannot determine OS version"
		exit 1
	fi
	
	. /etc/os-release
	if [[ "$NAME" != "Ubuntu" ]]; then
		print_warning "This script is designed for Ubuntu. Proceeding anyway..."
	else
		print_success "Ubuntu detected: $VERSION"
	fi
}

install_docker() {
	if command -v docker &> /dev/null; then
		print_success "Docker is already installed"
		return
	fi
	
	print_status "Installing Docker..."
	
	# Install prerequisites
	sudo apt-get update
	sudo apt-get install -y \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg \
		lsb-release
	
	# Add Docker's official GPG key
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
	
	# Add Docker repository
	echo \
		"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
		$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	
	# Install Docker Engine and Compose
	sudo apt-get update
	sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
	
	# Add current user to docker group
	sudo usermod -aG docker $USER
	
	print_success "Docker installed successfully"
	print_warning "You may need to log out and back in for Docker group permissions to take effect"
}

list_available_services() {
	echo "Available services:"
	for service_dir in services/*/; do
		service_name=$(basename "$service_dir")
		if [[ -f "$service_dir/setup.sh" ]]; then
			echo "  - $service_name"
		fi
	done
}

setup_service() {
	local service=$1
	local service_dir="services/$service"
	
	if [[ ! -d "$service_dir" ]]; then
		print_error "Service directory not found: $service_dir"
		return 1
	fi
	
	if [[ ! -f "$service_dir/setup.sh" ]]; then
		print_error "Setup script not found: $service_dir/setup.sh"
		return 1
	fi
	
	print_status "Setting up service: $service"
	
	# Run the service setup script (idempotent)
	bash "$service_dir/setup.sh"
	
	print_success "$service setup completed"
}

main() {
	print_status "Initializing My Home Server"
	echo ""
	
	check_root
	check_os
	
	install_docker
	echo ""
	
	if [[ $# -eq 0 ]]; then
		print_warning "No services specified"
		list_available_services
		echo ""
		echo "Usage: $0 <service1> [service2] [service3] ..."
		echo ""
		exit 0
	fi
	
	for service in "$@"; do
		setup_service "$service" || print_warning "Failed to setup $service"
		echo ""
	done
	
	print_success "All requested services have been initialized!"
	print_status "Start services with: docker-compose -f services/<service>/docker-compose.yml up -d"
}

main "$@"
