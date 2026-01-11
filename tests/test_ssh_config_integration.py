#!/usr/bin/env python
"""Integration tests for SSH config functionality with custom config files."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
def test_ssh_config_with_mac_based_hostnames():
  """Test SSH config with MAC-based hostnames in project .temp directory."""
  project_dir = Path(__file__).parent.parent  # Go up one level from tests/ to project root
  ssh_config_dir = project_dir / ".temp" / "ssh_configs"

  try:
    # Create the directory
    ssh_config_dir.mkdir(parents=True, exist_ok=True)
    assert ssh_config_dir.exists(), f"Failed to create SSH config directory: {ssh_config_dir}"

    # Create a test config file with MAC-based hostnames (our primary use case)
    test_config = ssh_config_dir / "AABBCCDDEEFF.config"
    test_config.write_text("""
# Ethernet           
Host example-device
  HostName 192.168.255.255 # example-device.lan
  User example-user
  Port 50022
  IdentityFile ~/.ssh/id_rsa_example
""")

    # Test that SSH can use this config with MAC-based hostname
    result = subprocess.run(
      ["ssh", "-F", str(test_config), "-G", "example-device"],
      capture_output=True,
      text=True,
      timeout=10,
    )

    assert result.returncode == 0, f"SSH config test failed: {result.stderr}"
    assert "hostname 192.168.255.255" in result.stdout.lower(), (
      "SSH hostname not found in config output"
    )
    assert "user example-user" in result.stdout.lower(), "SSH user not found in config output"
  except Exception as e:
    pytest.fail(f"Error with SSH config test: {e}")
