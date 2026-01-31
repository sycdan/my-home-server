import os
import shlex
import subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from mhs.config import LOCAL_ROOT

TEST_SERVICE_KEY = f"sandbox_{uuid.uuid4().hex[:8]}"
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


@dataclass
class Sandbox:
  root: Path
  service_key: str = TEST_SERVICE_KEY
  service_etc: Path = field(init=False)
  lib: Path = field(init=False)

  def __post_init__(self):
    os.environ["MHS_LOCAL_ROOT"] = str(self.root)
    self.write("fleet.json", TEST_FLEET_JSON)
    self.service_etc = self.root / "etc" / self.service_key
    self.service_etc.mkdir(parents=True)
    self.lib = self.root / "lib"
    self.lib.mkdir()

  def chdir(self):
    """switch back to the sandbox root directory"""
    os.chdir(self.root)

  def write(self, relpath: Path | str, content: str, **kwargs) -> Path:
    path = Path(relpath)
    if not path.is_absolute():
      path = self.root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, **kwargs)
    return path

  def read(self, relpath: str) -> str:
    return (self.root / relpath).read_text()

  def exists(self, relpath: str) -> bool:
    return (self.root / relpath).exists()

  def run(self, *args, **kwargs):
    return subprocess.run(
      args,
      cwd=self.root,
      text=True,
      capture_output=True,
      **kwargs,
    )

  def scaf_call(self, action, *args):
    return self.run(
      "scaf", shlex.quote(LOCAL_ROOT.as_posix()), "--call", shlex.quote(action), "--", *args
    )


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
  # automatically run tests *inside* the sandbox
  monkeypatch.chdir(tmp_path)
  return Sandbox(tmp_path)
