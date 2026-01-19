# Environment variable parsing helpers

# Normalize a boolean-like value into Bash true/false (0/1)
env_bool() {
  local val="${!1:-$2}"   # $1 = var name, $2 = default
  case "${val,,}" in
    1|true|t|yes|y|on) return 0 ;; # return code 0 == true
    0|false|f|no|n|off|"") return 1 ;; # return code 1 == false
    *)
      echo "Invalid boolean for $1: '$val'" >&2
      return 1
    ;;
  esac
}

# Get a string with optional default
env_str() {
  local val="${!1:-$2}"
  printf '%s' "$val"
}

# Parse an integer with optional default
env_int() {
  local val="${!1:-$2}"
  if [[ "$val" =~ ^-?[0-9]+$ ]]; then
    printf '%s' "$val"
  else
    echo "Invalid integer for $1: '$val'" >&2
    return 1
  fi
}

# Require a variable to be set (non-empty)
env_required() {
  local val="${!1}"
  if [[ -z "$val" ]]; then
    echo "Missing required environment variable: $1" >&2
    return 1
  fi
  printf '%s' "$val"
}

load_env() {
  local service_dir="$1"
  local env_file="$service_dir/.env"
  local example_file="$service_dir/example.env"
  
  if [[ ! -f "$env_file" ]]; then
    print_status "Creating .env file from example..."
    if [[ ! -f "$example_file" ]]; then
      print_error "Example environment file not found: $example_file"
      exit 1
    fi
    cp "$example_file" "$env_file"
    print_warning "Please edit $env_file and try your command again."
    exit 0
  fi
  
  print_status "Sourcing env vars from $env_file"
  source "$env_file"
}

