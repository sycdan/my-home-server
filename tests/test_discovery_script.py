import os
import subprocess
import tempfile

import pytest
from lib.discovery import generate_device_discovery_script


def test_generate_device_discovery_script_construction():
  hostname = "testdevice.lan"
  primary_mac = "AA:BB:CC:DD:EE:01"
  secondary_mac = "AA:BB:CC:DD:EE:02"
  script = generate_device_discovery_script(hostname, primary_mac, secondary_mac)

  # Check for DHCP lease lookup
  assert "/ip dhcp-server lease find where active-mac-address=$mac" in script
  # Check for ARP table lookup
  assert "/ip arp find where mac-address=$mac" in script
  # Check that both MACs are referenced
  assert primary_mac in script
  assert secondary_mac in script
  # Check that ping logic is present
  assert "/ping" in script


@pytest.mark.integration
def test_upload_and_run_discovery_script_on_router():
  hostname = "testdevice.lan"
  primary_mac = "AA:BB:CC:DD:EE:FF"  # fake
  secondary_mac = "6C:CD:D6:2A:9E:DD"  # real
  script_content = generate_device_discovery_script(
    hostname, primary_mac, secondary_mac
  )
  script_name = "pytest-discover-test.rsc"
  router_host = "router"

  def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)

  # Write script to a temp file
  with tempfile.NamedTemporaryFile("w", delete=False) as f:
    f.write(script_content)
    local_script_path = f.name

  try:
    # Upload script to router
    scp_cmd = ["scp", local_script_path, f"{router_host}:/{script_name}"]
    run(scp_cmd)

    # Run script on router
    ssh_cmd = ["ssh", router_host, f"/import {script_name}"]
    result = run(ssh_cmd)
    assert "=== Complete ===" in result.stdout

    # Cleanup
    run(["ssh", router_host, f'/file remove "{script_name}"'])
    run(["ssh", router_host, f'/ip dns static remove [find where name="{hostname}"]'])
  finally:
    os.remove(local_script_path)
