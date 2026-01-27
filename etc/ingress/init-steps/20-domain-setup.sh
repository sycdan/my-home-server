main() {
	local error_count=0

	for DOMAIN in "${VALID_DOMAINS[@]}"; do
		print_status "Configuring domain: $DOMAIN"
		# Process all services for this domain
		for service in "${SERVICES[@]}"; do
			FULL_HOSTNAME="${service%%|*}"

			# Skip if not for this domain
			if [[ ! "$FULL_HOSTNAME" == *"$DOMAIN" ]]; then
				continue
			fi

			# Extract subdomain
			SUBDOMAIN=$(echo "$FULL_HOSTNAME" | sed "s/\.$DOMAIN$//")

			print_status "Setting up: $FULL_HOSTNAME -> $MHS_CNAME_TARGET"

			# Check if CNAME already exists
			EXISTING_CNAME=$(dig +short $FULL_HOSTNAME CNAME 2>/dev/null | head -1)
			if [[ "$EXISTING_CNAME" == "$MHS_CNAME_TARGET." ]]; then
				print_success "CNAME already configured: $FULL_HOSTNAME"
				((success_count++))
				continue
			fi

			# Create CNAME record via Porkbun API
			API_RESPONSE=$(curl -s -X POST "https://api.porkbun.com/api/json/v3/dns/create/$DOMAIN" \
				-H "Content-Type: application/json" \
				-d "{\n                \"apikey\": \"$PORKBUN_API_KEY\",\n                \"secretapikey\": \"$PORKBUN_SECRET_KEY\",\n                \"name\": \"$SUBDOMAIN\",\n                \"type\": \"CNAME\",\n                \"content\": \"$CNAME_TARGET\",\n                \"ttl\": \"300\"\n            }")

			if echo "$API_RESPONSE" | grep -q '"status":"SUCCESS"'; then
				print_success "CNAME created: $FULL_HOSTNAME"
				((success_count++))
			elif echo "$API_RESPONSE" | grep -q "Domain is not opted in to API access"; then
				print_error "Domain $DOMAIN is not opted in to API access"
				echo "  Enable at: https://porkbun.com/account/domainsSpeedy"
				((error_count++))
			else
				ERROR_MSG=$(echo "$API_RESPONSE" | grep -o '"message":"[^"]*' | cut -d'"' -f4)
				print_error "API error for $FULL_HOSTNAME: $ERROR_MSG"
				((error_count++))
			fi
		done
	done

	if [[ $error_count -gt 0 ]]; then
		print_warning "Some domains had errors. Check configuration and try again."
		exit 1
	fi
}

main