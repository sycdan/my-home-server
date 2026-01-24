echo "KOPIA_SERVER_USERNAME=${KOPIA_CONTROL_USERNAME}"
echo "KOPIA_SERVER_PASSWORD=${KOPIA_CONTROL_PASSWORD}"
./bin/kopia server status --server-control-username="${KOPIA_CONTROL_USERNAME}" --server-control-password="${KOPIA_CONTROL_PASSWORD}" || echo "failed"


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