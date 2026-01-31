import os
import sys

import pytest

from tests.conftest import Sandbox

pytestmark = pytest.mark.integration


def test(sandbox: Sandbox):
  """Happy-path test for remote service command execution on a real host."""
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

  result = sandbox.scaf_call(
    "mhs/control/execute_service_script/",
    init_script.relative_to(sandbox.root).as_posix(),
  )
  assert result.returncode == 0, f"Command failed: {result.stderr}"
