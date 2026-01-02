#!/bin/bash

# Home Server Service Controller
# Utility script to manage multiple services

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

print_error() {
	echo -e "${RED}[ERROR]${NC} $1" >&2
}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

show_usage() {
	echo "Usage: $0 <command> [service] [options]"
	echo ""
	echo "Global Commands:"
	echo "  status                      Show status of all services"
	echo "  list                        List all available services"
	echo ""
	echo "Service Commands:"
	echo "  up <service> [options]      Start a service (docker compose up -d)"
	echo "  down <service> [options]    Stop a service (docker compose down)"
	echo "  restart <service> [options] Restart a service"
	echo "  logs <service> [options]    View service logs (follow mode)"
	echo "  ps <service>                Show service containers status"
	echo "  shell <service>             Open shell in service directory"
	echo ""
	echo "Example:"
	echo "  $0 up immich"
	echo "  $0 logs immich -n 100"
	echo "  $0 down immich"
	echo "  $0 status"
}

list_services() {
	print_status "Available services:"
	for service_dir in "$SCRIPT_DIR/services"/*/; do
		service_name=$(basename "$service_dir")
		if [[ -f "$service_dir/docker-compose.yml" ]]; then
			echo "  - $service_name"
		fi
	done
}

validate_service() {
	local service=$1
	local service_dir="$SCRIPT_DIR/services/$service"
	
	if [[ ! -d "$service_dir" ]]; then
		print_error "Service directory not found: $service_dir"
		return 1
	fi
	
	if [[ ! -f "$service_dir/docker-compose.yml" ]]; then
		print_error "docker-compose.yml not found in $service_dir"
		return 1
	fi
	
	if [[ ! -f "$service_dir/.env" ]]; then
		print_error ".env file not found in $service_dir"
		print_status "Run 'bash init $service' to initialize the service"
		return 1
	fi
	
	return 0
}

service_up() {
	local service=$1
	shift
	
	validate_service "$service" || return 1
	
	print_status "Starting $service..."
	cd "$SCRIPT_DIR/services/$service"
	docker compose up -d "$@"
	print_success "$service is running"
}

service_down() {
	local service=$1
	shift
	
	validate_service "$service" || return 1
	
	print_status "Stopping $service..."
	cd "$SCRIPT_DIR/services/$service"
	docker compose down "$@"
	print_success "$service stopped"
}

service_restart() {
	local service=$1
	shift
	
	validate_service "$service" || return 1
	
	print_status "Restarting $service..."
	cd "$SCRIPT_DIR/services/$service"
	docker compose restart "$@"
	print_success "$service restarted"
}

service_logs() {
	local service=$1
	shift
	
	validate_service "$service" || return 1
	
	print_status "Showing logs for $service..."
	cd "$SCRIPT_DIR/services/$service"
	docker compose logs -f "$@"
}

service_ps() {
	local service=$1
	
	validate_service "$service" || return 1
	
	cd "$SCRIPT_DIR/services/$service"
	docker compose ps
}

service_status() {
	for service_dir in "$SCRIPT_DIR/services"/*/; do
		service_name=$(basename "$service_dir")
		if [[ -f "$service_dir/docker-compose.yml" && -f "$service_dir/.env" ]]; then
			print_status "Service status for $service_name:"
			cd "$service_dir"
			docker compose ps
			echo ""
		fi
	done
}

service_shell() {
	local service=$1
	local service_dir="$SCRIPT_DIR/services/$service"
	
	if [[ ! -d "$service_dir" ]]; then
		print_error "Service directory not found: $service_dir"
		return 1
	fi
	
	print_status "Opening shell in $service_dir..."
	cd "$service_dir"
	bash
}

main() {
	if [[ $# -lt 1 ]]; then
		show_usage
		exit 1
	fi
	
	local command=$1
	shift
	
	case "$command" in
		up|down|restart|logs|ps|shell)
			# Service-specific commands require a service argument
			if [[ $# -lt 1 ]]; then
				print_error "Service required for command '$command'"
				show_usage
				exit 1
			fi
			
			local service=$1
			shift
			
			if [[ ! -d "$SCRIPT_DIR/services/$service" ]]; then
				print_error "Unknown service: $service"
				list_services
				exit 1
			fi
			
			service_$command "$service" "$@"
			;;
		status)
			service_status
			;;
		list)
			list_services
			;;
		help|--help|-h)
			show_usage
			;;
		*)
			print_error "Unknown command: $command"
			show_usage
			exit 1
			;;
	esac
}

main "$@"
