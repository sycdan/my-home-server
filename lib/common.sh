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