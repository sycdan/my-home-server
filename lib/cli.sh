# Usage: define a main() function in the service script then source this file.

# Enable strict error handling
set -euo pipefail

# Set up standard paths based on directory structure from the calling service
script_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
if [[ "$script_dir" == */services/*/bin ]]; then
  export SERVICE_DIR="$(cd "$script_dir/../" && pwd)"
  elif [[ "$script_dir" == */services/* ]] && [[ "$script_dir" != */services/*/bin ]]; then
  export SERVICE_DIR="$script_dir"
else
  echo "Error: Script must be in services/<service>/ or services/<service>/bin/ directory" >&2
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

# Invoke caller's main function
if [[ "${BASH_SOURCE[0]}" != "${BASH_SOURCE[1]}" ]]; then
  if ! declare -f main > /dev/null 2>&1; then
    echo "Error: main() function not defined in script" >&2
    exit 1
  fi
  
  # Call main with all script arguments
  main "$@"
fi