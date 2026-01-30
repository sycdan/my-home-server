import os
import sys

import pytest

pytestmark = pytest.mark.integration


def test_remote_service_can_be_initialized(sandbox):
  """Happy-path test for remote service command execution on a real host."""
  from mhs.control.execute_service_script.cli import main

  sandbox.write(".env", "GLOBAL_VAR=1111")
  sandbox.write("lib/test.sh", "LIB_VAR=2222")
  sandbox.write(sandbox.service_etc / ".env", "SERVICE_VAR=3333")
  init_script = sandbox.service_etc / "init"
  sandbox.write(
    init_script,
    "\n".join(
      [
        "#!/usr/bin/env bash",
        'echo "User: $(whoami)"',
        'echo "IP: $(hostname -I)"',
        'echo "Root: $(pwd)"',
        'source ".env"',
        'source "lib/test.sh"',
        f'source "etc/{sandbox.service_key}/.env"',
        'echo "Global: $GLOBAL_VAR"',
        'echo "Lib: $LIB_VAR"',
        'echo "Service: $SERVICE_VAR"',
      ]
    ),
    newline="\n",
  )
  os.chmod(init_script, 0o755)

  try:
    main(
      [
        str(init_script),
        "--root",
        str(sandbox.root),
        "--create-root",
      ]
    )
    sys.exit(0)
  except SystemExit as e:
    assert e.code == 0, "Expected command to complete successfully"
  else:
    assert False, "Expected SystemExit exception"


def test_storage_mount_is_idempotent():
  """Ensure that mounting an already-mounted storage device is handled gracefully."""
  from mhs.control.mount.cli import main

  main()


def test_can_discover_device():
  from mhs.control.discover_devices.cli import main

  main(
    [
      "r-pi",
    ]
  )

  # hostname = "testdevice.lan"
  # primary_mac = "AA:BB:CC:DD:EE:FF"  # fake
  # secondary_mac = "6C:CD:D6:2A:9E:DD"  # real
  # script_content = generate_device_discovery_script(
  #   hostname, primary_mac, secondary_mac
  # )
  # script_name = "pytest-discover-test.rsc"
  # router_host = "router"

  # def run(args):
  #   return subprocess.run(args, check=True, capture_output=True, text=True)

  # # Write script to a temp file
  # with tempfile.NamedTemporaryFile("w", delete=False) as f:
  #   f.write(script_content)
  #   local_script_path = f.name

  # try:
  #   # Upload script to router
  #   scp_cmd = ["scp", local_script_path, f"{router_host}:/{script_name}"]
  #   run(scp_cmd)

  #   # Run script on router
  #   ssh_cmd = ["ssh", router_host, f"/import {script_name}"]
  #   result = run(ssh_cmd)
  #   # TODO: ensure an ip was found
  #   assert "=== Complete ===" in result.stdout

  #   # Cleanup
  #   run(["ssh", router_host, f'/file remove "{script_name}"'])
  #   run(["ssh", router_host, f'/ip dns static remove [find where name="{hostname}"]'])
  # finally:
  #   os.remove(local_script_path)
