#!/usr/bin/env bash

# Check if server is already running
container_status=$(./bin/ctl ps)
if ! echo "$container_status" | grep -q "kopia.*Up"; then
  print_status "Starting container..."
  ./bin/ctl up -d
fi

# Wait for Kopia CLI to come up, if necessary
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
  # Test if server can respond to actual Kopia commands
  if ./bin/kopia help >/dev/null 2>&1; then
    break
  fi
  
  attempt=$((attempt + 1))
  if [ $attempt -eq $max_attempts ]; then
    print_error "Kopia failed to respond to commands for 60 seconds"
    print_status "Checking container status:"
    ./bin/ctl ps
    print_status "Recent logs:"
    ./bin/ctl logs --tail=10
    exit 1
  fi
  
  echo -n "."
  sleep 2
done

print_success "Kopia is ready to accept commands."

