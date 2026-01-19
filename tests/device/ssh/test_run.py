import os
import sys
import tempfile
from pathlib import Path

import pytest
from mhs.device.ssh.run.handler import main

TEST_SERVICE_LABEL = "testing"
TEST_FLEET_JSON = """
{
	"devices": {
		"r-pi": {
			"description": "Raspberry Pi 3",
			"ssh_host": "ingress",
			"macs": ["B8:27:EB:AB:C0:DC"],
			"services": {
				"<<service-label>>": {
					"port": 59999
				}
			}
		}
	}
}
""".strip().replace("<<service-label>>", TEST_SERVICE_LABEL)


@pytest.mark.integration
def test_e2e():
  """Happy-path test for remote service command execution on a real host."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)

    test_fleet_file = root_dir / "fleet.json"
    test_fleet_file.write_text(TEST_FLEET_JSON)

    test_service_dir = root_dir / "services" / TEST_SERVICE_LABEL
    test_service_dir.mkdir(parents=True)
    test_lib_dir = root_dir / "lib"
    test_lib_dir.mkdir()

    test_global_env_file = root_dir / ".env"
    test_global_env_file.write_text("GLOBAL_VAR=1111")
    test_lib_file = test_lib_dir / "test.sh"
    test_lib_file.write_text("LIB_VAR=2222")
    test_service_env_file = test_service_dir / ".env"
    test_service_env_file.write_text("SERVICE_VAR=3333")
    test_service_command_file = test_service_dir / "init"
    test_service_command_file.write_text(
      "\n".join(
        [
          "#!/usr/bin/env bash",
          'echo "User: $(whoami)"',
          'echo "IP: $(hostname -I)"',
          'echo "Root: $(pwd)"',
          'source ".env"',
          'source "lib/test.sh"',
          f'source "services/{TEST_SERVICE_LABEL}/.env"',
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
