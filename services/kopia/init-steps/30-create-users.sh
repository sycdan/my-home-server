
# #!/usr/bin/env bash

# # Check if repository exists, create it if not
# if ! ./bin/kopia repository status >/dev/null 2>&1; then
#   print_status "Creating new repository..."
#   ./bin/kopia repository create filesystem --path=/repository
# else
#   print_success "Repository already exists"
# fi

# # Create admin user (using control credentials)
# print_status "Creating admin user: dan@${KOPIA_HOSTNAME}..."
# if ! ./bin/kopia server user add "dan@${KOPIA_HOSTNAME}" --user-password="${KOPIA_REPOSITORY_PASSWORD}"; then
#   print_warning "User may already exist or creation failed"
# fi

# # Give admin user full access
# print_status "Setting admin user permissions..."
# ./bin/kopia server acl add --user "dan@${KOPIA_HOSTNAME}" --access FULL

# print_success "User setup complete!"
# print_status "You can now connect clients using:"
# echo "  Username: dan@${KOPIA_HOSTNAME}"
# echo "  Password: ${KOPIA_REPOSITORY_PASSWORD}"
# echo "  Server URL: http://$(hostname):51515"