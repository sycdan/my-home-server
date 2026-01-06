#!/bin/bash
# Generates discovery.rsc script from SERVICES array in lib/services.sh
# This ensures split DNS entries stay in sync with the services configuration

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../../" && pwd )"
source "$ROOT_DIR/lib/common.sh"
source "$ROOT_DIR/lib/services.sh"

print_status "Generating discovery.rsc split DNS entries..."

# Create the split DNS section
cat > "$SCRIPT_DIR/scripts/split-dns-entries.rsc" << 'EOF'
# Auto-generated split DNS entries - DO NOT EDIT MANUALLY
# Regenerate with: ./devices/mikrotek-hex/generate-discovery.sh
# This section should be placed in the "Updating Split DNS Entries" section of discovery.rsc

# Update split DNS entries for external domains to point to reverse proxy internally
:if ($rpResult != "") do={
  :local rpIp ($rpResult->0)
  
  # List of external domains that should resolve to the reverse proxy internally
  :local externalDomains {
EOF

# Add each domain from SERVICES array
while IFS= read -r domain; do
  echo "    \"$domain\"" >> "$SCRIPT_DIR/scripts/split-dns-entries.rsc"
done < <(get_external_domains | sort)

cat >> "$SCRIPT_DIR/scripts/split-dns-entries.rsc" << 'EOF'
  }
  
  # Remove old split DNS entries
  /ip dns static remove [find comment~"Split DNS"]
  
  # Add new entries pointing to reverse proxy IP
  :foreach domain in=$externalDomains do={
    :put "Split DNS: $domain -> $rpIp"
    /ip dns static add name=$domain address=$rpIp comment="Split DNS" ttl=5m
  }
} else={
  :put "ERROR: Reverse proxy IP not found, skipping split DNS update"
}
EOF

print_success "Generated split DNS entries to: $SCRIPT_DIR/scripts/split-dns-entries.rsc"
echo ""
echo "To update discovery.rsc:"
echo "1. Open $SCRIPT_DIR/scripts/discovery.rsc"
echo "2. Find the section: '==== Updating Split DNS Entries ===='  "
echo "3. Replace it with the content from: $SCRIPT_DIR/scripts/split-dns-entries.rsc"
echo ""
echo "Or copy this section to update manually:"
echo "---"
cat "$SCRIPT_DIR/scripts/split-dns-entries.rsc"
echo "---"
