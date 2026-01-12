import shutil
import subprocess
import uuid

import pytest

from mhs.config import BASE_DOMAIN, PYTHON, ROOT_DIR
from mhs.create_action.logic import CreateActionRequest, handle


@pytest.mark.integration
def test_create_action_basic():
  """Test that a new action can be created with minimal input."""
  domain_dir = ROOT_DIR / BASE_DOMAIN / "examples" / f"x{uuid.uuid4().hex}"
  assert not domain_dir.exists()

  domain_path = domain_dir.relative_to(ROOT_DIR).as_posix()
  req = CreateActionRequest(action_name="Do Stuff", domain_path=domain_path)
  resp = handle(req)
  assert not resp.errors, f"Errors: {resp.errors}"

  # Verify expected structure and files
  py_dir = ROOT_DIR / domain_path / "do_stuff"
  proto_dir = ROOT_DIR / "proto" / domain_path / "do_stuff"
  test_dir = ROOT_DIR / "tests" / domain_path / "do_stuff"
  assert py_dir.is_dir(), f"Missing {py_dir}"
  assert proto_dir.is_dir(), f"Missing {proto_dir}"
  assert test_dir.is_dir(), f"Missing {test_dir}"
  assert (py_dir / "__init__.py").is_file(), "Missing __init__.py"
  assert (py_dir / "logic.py").is_file(), "Missing logic.py"
  assert (proto_dir / "messages.proto").is_file(), "Missing messages.proto"
  assert (test_dir / "test_logic.py").is_file(), "Missing test_logic.py"
  assert (test_dir / "__init__.py").is_file(), "Missing test __init__.py"

  # Invoke the new action
  action_path = py_dir.relative_to(ROOT_DIR).as_posix()
  subprocess.run([PYTHON, "call", action_path], check=True)

  # Clean up
  shutil.rmtree(domain_dir, ignore_errors=True)
  shutil.rmtree(proto_dir, ignore_errors=True)
  shutil.rmtree(test_dir, ignore_errors=True)
