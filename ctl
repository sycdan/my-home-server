#!/bin/bash

# Utility script to manage individual services

set -e

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$ROOT_DIR/lib/common.sh"

show_usage() {
	local service=$1
	
	if [[ -z "$service" ]]; then
		# Full usage
		echo "Usage: $0 <service|all> <command> [options]"
		echo ""
		echo "Service Commands:"
		echo "  <service> up [options]      Start a service (docker compose up -d)"
		echo "  <service> down [options]    Stop a service (docker compose down)"
		echo "  <service> restart [options] Restart a service"
		echo "  <service> logs [options]    View service logs (follow mode)"
		echo "  <service> ps                Show service containers status"
		echo "  <service> shell             Open shell in service directory"
		echo ""
		echo "Global Commands (service 'all'):"
		echo "  all list                    List all available services"
		echo "  all status                  Show status of all services"
		echo ""
		echo "Example:"
		echo "  $0 immich up"
		echo "  $0 immich logs -n 100"
		echo "  $0 immich down"
		echo "  $0 all status"
	elif [[ "$service" == "all" ]]; then
		# Global usage
		echo "Usage: $0 all <command>"
		echo ""
		echo "Global Commands:"
		echo "  all list                    List all available services"
		echo "  all status                  Show status of all services"
	else
		# Service-specific usage
		echo "Usage: $0 $service <command> [options]"
		echo ""
		echo "Service Commands:"
		echo "  $service up [options]       Start the service (docker compose up -d)"
		echo "  $service down [options]     Stop the service (docker compose down)"
		echo "  $service restart [options]  Restart the service"
		echo "  $service logs [options]     View service logs (follow mode)"
		echo "  $service ps                 Show service containers status"
		echo "  $service shell              Open shell in service directory"
	fi
}

# Helper to run docker compose commands in service directory
run_compose() {
	local service=$1
	local action=$2
	shift 2
	
	validate_service "$service" || return 1
	
	case "$action" in
		up)
			print_status "Starting $service..."
			cd "$ROOT_DIR/services/$service"
			docker compose up -d "$@"
			print_success "$service is running"
			;;
		down)
			print_status "Stopping $service..."
			cd "$ROOT_DIR/services/$service"
			docker compose down "$@"
			print_success "$service stopped"
			;;
		restart)
			print_status "Restarting $service..."
			cd "$ROOT_DIR/services/$service"
			docker compose restart "$@"
			print_success "$service restarted"
			;;
		logs)
			print_status "Showing logs for $service..."
			cd "$ROOT_DIR/services/$service"
			docker compose logs -f "$@"
			;;
		ps)
			cd "$ROOT_DIR/services/$service"
			docker compose ps
			;;
	esac
}

list_services() {
	print_status "Available services:"
	for service_dir in "$ROOT_DIR/services"/*/; do
		service_name=$(basename "$service_dir")
		if [[ -f "$service_dir/docker-compose.yml" ]]; then
			echo "  - $service_name"
		fi
	done
}

validate_service() {
	local service=$1
	local service_dir="$ROOT_DIR/services/$service"
	
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
	run_compose "$1" up "$@"
}

service_down() {
	run_compose "$1" down "$@"
}

service_restart() {
	run_compose "$1" restart "$@"
}

service_logs() {
	run_compose "$1" logs "$@"
}

service_ps() {
	run_compose "$1" ps
}

service_status() {
	for service_dir in "$ROOT_DIR/services"/*/; do
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
	local service_dir="$ROOT_DIR/services/$service"
	
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
	
	local service=$1
	
	# If only one arg and it's not a valid service or "all", show full usage
	if [[ $# -lt 2 ]]; then
		if [[ "$service" == "all" ]]; then
			show_usage "all"
		elif [[ -d "$ROOT_DIR/services/$service" ]]; then
			show_usage "$service"
		else
			show_usage
		fi
		exit 1
	fi
	
	local command=$2
	shift 2
	
	# Handle global commands
	if [[ "$service" == "all" ]]; then
		case "$command" in
			status)
				service_status
				;;
			list)
				list_services
				;;
			help|--help|-h)
				show_usage "all"
				;;
			*)
				print_error "Unknown command: $command"
				show_usage "all"
				exit 1
				;;
		esac
	else
		# Handle service-specific commands
		if [[ ! -d "$ROOT_DIR/services/$service" ]]; then
			print_error "Unknown service: $service"
			list_services
			exit 1
		fi
		
		case "$command" in
			up|down|restart|logs|ps)
				service_$command "$service" "$@"
				;;
			shell)
				cd "$ROOT_DIR/services/$service"
				bash
				;;
			*)
				print_error "Unknown command: $command"
				show_usage "$service"
				exit 1
				;;
		esac
	fi
}

main "$@"
