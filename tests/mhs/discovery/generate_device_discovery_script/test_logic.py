import os
import subprocess
import tempfile

import pytest

from mhs.discovery.generate_device_discovery_script.logic import (
  GenerateDiscoveryScriptRequest,
  handle,
)


@pytest.mark.integration
def test_upload_and_run_discovery_script_on_router():
  hostname = "testdevice.lan"
  primary_mac = "AA:BB:CC:DD:EE:FF"  # fake
  secondary_mac = "6C:CD:D6:2A:9E:DD"  # real
  request = GenerateDiscoveryScriptRequest(
    hostname=hostname, primary_mac=primary_mac, secondary_mac=secondary_mac
  )
  script_content = handle(request).script_content
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
    assert result.stdout.strip().endswith("executed successfully")
    assert "Using IP" in result.stdout

    # Cleanup
    run(["ssh", router_host, f'/file remove "{script_name}"'])
    run(["ssh", router_host, f'/ip dns static remove [find where name="{hostname}"]'])
  finally:
    os.remove(local_script_path)
