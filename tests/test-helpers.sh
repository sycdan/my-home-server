#!/bin/bash
# Test script to demonstrate and verify SERVICES array helpers

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
source "$ROOT_DIR/lib/common.sh"
source "$ROOT_DIR/lib/services.sh"

# Test counters
tests_run=0
tests_passed=0
tests_failed=0

# Helper function for assertions
assert_equals() {
  local test_name=$1
  local expected=$2
  local actual=$3
  
  ((tests_run++))
  
  if [[ "$expected" == "$actual" ]]; then
    print_success "✓ $test_name"
    ((tests_passed++))
  else
    print_error "✗ $test_name"
    echo "  Expected: $expected"
    echo "  Got:      $actual"
    ((tests_failed++))
  fi
}

assert_contains() {
  local test_name=$1
  local haystack=$2
  local needle=$3
  
  ((tests_run++))
  
  # Support regex patterns (if needle contains ^, it's a regex)
  if [[ "$needle" =~ ^[\^] ]]; then
    if echo "$haystack" | grep -E "$needle" > /dev/null; then
      print_success "✓ $test_name"
      ((tests_passed++))
    else
      print_error "✗ $test_name"
      echo "  Expected pattern: $needle"
      echo "  In: $haystack"
      ((tests_failed++))
    fi
  else
    # Simple substring match
    if echo "$haystack" | grep -q "$needle"; then
      print_success "✓ $test_name"
      ((tests_passed++))
    else
      print_error "✗ $test_name"
      echo "  Expected to find: $needle"
      echo "  In: $haystack"
      ((tests_failed++))
    fi
  fi
}

echo ""
print_status "Running SERVICES array helper tests"
echo ""

# Test 1: SERVICES array contains expected entries
first_service="${SERVICES[0]}"
assert_equals "First service is photos subdomain" "photos.wildharvesthomestead.com|immich.lan|2283" "$first_service"

# Test 2: Second service format
second_service="${SERVICES[1]}"
assert_equals "Second service is stream subdomain" "stream.wildharvesthomestead.com|jellyfin.lan|8096" "$second_service"

# Test 3: get_ingress_domains returns exactly one base domain
domains=$(get_ingress_domains)
domain_count=$(echo "$domains" | wc -l)
assert_equals "get_ingress_domains returns exactly 1 base domain" "1" "$domain_count"

# Test 4: get_ingress_domains returns the correct base domain
assert_equals "get_ingress_domains returns wildharvesthomestead.com" "wildharvesthomestead.com" "$(get_ingress_domains)"

# Test 5: get_external_domains returns exactly 2 full subdomains
external=$(get_external_domains)
external_count=$(echo "$external" | wc -l)
assert_equals "get_external_domains returns exactly 2 subdomains" "2" "$external_count"

# Test 6: get_external_domains returns exact photos subdomain
external_sorted=$(get_external_domains | sort)
assert_contains "get_external_domains includes photos.wildharvesthomestead.com (exact)" "$external_sorted" "^photos.wildharvesthomestead.com$"

# Test 7: get_external_domains returns exact stream subdomain
assert_contains "get_external_domains includes stream.wildharvesthomestead.com (exact)" "$external_sorted" "^stream.wildharvesthomestead.com$"

# Test 8: CNAME_TARGET is set correctly
assert_equals "CNAME_TARGET is home.sycdan.com" "home.sycdan.com" "$CNAME_TARGET"

echo ""
print_status "Test Summary"
echo "  Passed: $tests_passed / $tests_run"
if [[ $tests_failed -gt 0 ]]; then
  print_error "  Failed: $tests_failed"
  exit 1
else
  print_success "  All tests passed!"
fi
