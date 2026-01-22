# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
  echo -e "${BLUE}ℹ️ ${NC} $1"
}

print_success() {
  echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠️ ${NC} $1" >&2
}

print_error() {
  echo -e "${RED}❌ ${NC} $1" >&2
}

is_true() {
  case "${1,,}" in
    1|true|yes|y|on)  return 0 ;;  # true
    0|false|no|n|off|"") return 1 ;; # false
    *)
      echo "Invalid boolean value: '$1'" >&2
      return 1
    ;;
  esac
}

# Usage: split_csv "a,b,c" array_var
split_csv() {
  local input="$1"
  local __resultvar="$2"
  IFS=',' read -ra tmp <<< "$input"
  eval "$__resultvar=(\"\${tmp[@]}\")"
}

# Usage: parse_opt variable_name expected_arg default_value [args...]
parse_opt() {
  local var_name="$1"
  local expected_flag="--$2"
  local default_val="$3"
  shift 3
  local args=("$@")
  
  local val=""
  local found=false

  local i=0
  while [[ $i -lt ${#args[@]} ]]; do
    case "${args[$i]}" in
      ${expected_flag}=*)
         val="${args[$i]#*=}"
         found=true
         break
         ;;
      ${expected_flag})
         # Check if next arg is a value or another flag
         if [[ $((i+1)) -lt ${#args[@]} ]] && [[ "${args[$((i+1))]}" != --* ]]; then
           val="${args[$((i+1))]}"
           found=true
           break
         else
           # Flag present but no value. Assume boolean true if that matches intent, 
           # or empty string if just checking presence.
           val="true" 
           found=true
           break
         fi
         ;;
    esac
    ((i++))
  done

  if [[ "$found" == "false" ]]; then
    if [[ "$default_val" == "REQUIRED" ]]; then
      print_error "Missing required argument: $expected_flag"
      exit 1
    fi
    val="$default_val"
  fi

  printf -v safe_val %q "$val"
  eval "$var_name=$safe_val"
}
