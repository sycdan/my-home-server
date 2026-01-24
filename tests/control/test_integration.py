import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

TEST_SERVICE_KEY = f"svc_{uuid.uuid4().hex[:8]}"
TEST_FLEET_JSON = """
{
  "media": {
    "mmcblk0p2": {
      "uuid": "1232a209-2596-48f0-a078-731d10b918ad",
      "description": "Already mounted to /"
    }
  },
	"devices": {
		"r-pi": {
			"description": "Raspberry Pi 3",
			"ssh_host": "ingress",
			"macs": ["B8:27:EB:AB:C0:DC"],
			"services": {
				"{{service-key}}": {
					"port": 59999
				}
			}
		}
	}
}
""".strip().replace("{{service-key}}", TEST_SERVICE_KEY)


@pytest.fixture()
def fake_tree():
  """Fixture to set LOCAL_ROOT to a temporary directory for tests."""
  with tempfile.TemporaryDirectory() as temp_dir:
    original_local_root = os.environ.get("MHS_LOCAL_ROOT")
    os.environ["MHS_LOCAL_ROOT"] = temp_dir
    root_dir = Path(temp_dir)

    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text(TEST_FLEET_JSON)

    service_dir = root_dir / "services" / TEST_SERVICE_KEY
    service_dir.mkdir(parents=True)

    lib_dir = root_dir / "lib"
    lib_dir.mkdir()

    try:
      yield root_dir, lib_dir, service_dir
    finally:
      if original_local_root is not None:
        os.environ["MHS_LOCAL_ROOT"] = original_local_root
      else:
        del os.environ["MHS_LOCAL_ROOT"]


def test_remote_service_can_be_initialized(fake_tree):
  """Happy-path test for remote service command execution on a real host."""
  from mhs.control.execute_service_script.cli import main

  root_dir, lib_dir, service_dir = fake_tree

  global_env_file = root_dir / ".env"
  global_env_file.write_text("GLOBAL_VAR=1111")

  test_lib_file = lib_dir / "test.sh"
  test_lib_file.write_text("LIB_VAR=2222")

  test_service_env_file = service_dir / ".env"
  test_service_env_file.write_text("SERVICE_VAR=3333")
  test_service_command_file = service_dir / "init"
  test_service_command_file.write_text(
    "\n".join(
      [
        "#!/usr/bin/env bash",
        'echo "User: $(whoami)"',
        'echo "IP: $(hostname -I)"',
        'echo "Root: $(pwd)"',
        'source ".env"',
        'source "lib/test.sh"',
        f'source "services/{TEST_SERVICE_KEY}/.env"',
        'echo "Global: $GLOBAL_VAR"',
        'echo "Lib: $LIB_VAR"',
        'echo "Service: $SERVICE_VAR"',
      ]
    ),
    newline="\n",
  )
  os.chmod(test_service_command_file, 0o755)

  try:
    main(
      [
        str(test_service_command_file),
        "--root",
        str(root_dir),
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
