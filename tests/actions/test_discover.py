import sys
import tempfile
from pathlib import Path

import pytest
from lib.actions.discover import core

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
  """Happy-path test for device discovery."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)

    try:
      core.main(
        [
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
