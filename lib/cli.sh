# Usage: define a main() function in the service script then source this file.

# Make bootstrapping idempotent
if [[ -z "${MHS_CLI_BOOTSTRAPPED:-}" ]]; then
  # Enable strict error handling
  set -euo pipefail
  
  # Set up standard paths based on directory structure from the calling service
  script_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
  echo $script_dir
  if [[ "$script_dir" == */etc/*/bin ]]; then
    export SERVICE_DIR="$(cd "$script_dir/../" && pwd)"
    elif [[ "$script_dir" == */etc/* ]] && [[ "$script_dir" != */etc/*/bin ]]; then
    export SERVICE_DIR="$script_dir"
  else
    echo "Error: Script must be in etc/<service>/ or etc/<service>/bin/ directory" >&2
    exit 1
  fi
  export SERVICE_KEY="$(basename "$SERVICE_DIR")"
  export ROOT_DIR="$(cd "$SERVICE_DIR/../../" && pwd)"
  export LIB_DIR="$ROOT_DIR/lib"
  
  # Source common libraries
  source "$LIB_DIR/common.sh"
  source "$LIB_DIR/services.sh"
  source "$LIB_DIR/env.sh"
  
  # Load environment variables
  load_env "$ROOT_DIR"
  load_env "$SERVICE_DIR"
  
  export MHS_CLI_BOOTSTRAPPED=1
fi

# Invoke main() in the caller
if [[ "${BASH_SOURCE[0]}" != "${BASH_SOURCE[1]}" ]]; then
  if ! declare -f main > /dev/null 2>&1; then
    echo "Error: main() function not defined in script" >&2
    exit 1
  fi
  main "$@"
fi