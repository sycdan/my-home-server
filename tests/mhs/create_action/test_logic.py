import shutil
import subprocess
import uuid

import pytest

from mhs.config import BASE_DOMAIN, PYTHON, ROOT_DIR
from mhs.create_action.logic import CreateActionRequest, handle


@pytest.fixture(autouse=True)
def cleanup_example_dirs():
  """Automatically clean up any leftover example directories after each test."""
  yield  # Run the test
  # Cleanup after test regardless of success/failure
  for pattern in ["mhs/examples/x*", "proto/mhs/examples/x*", "tests/mhs/examples/x*"]:
    for path in ROOT_DIR.glob(pattern):
      if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


def test_create_action_fails_when_proto_file_already_exists():
  domain_dir = ROOT_DIR / BASE_DOMAIN / "examples" / f"x{uuid.uuid4().hex}"
  domain_path = domain_dir.relative_to(ROOT_DIR).as_posix()

  # Create the proto directory and file first
  proto_dir = ROOT_DIR / "proto" / domain_path / "test_action"
  proto_dir.mkdir(parents=True, exist_ok=True)
  (proto_dir / "messages.proto").write_text("existing content")

  req = CreateActionRequest(action_name="Test Action", domain_path=domain_path)
  resp = handle(req)
  assert resp.errors, "Expected error when proto file exists"
  assert "already exists" in resp.errors[0]


def test_create_action_handles_existing_files_gracefully():
  domain_dir = ROOT_DIR / BASE_DOMAIN / "examples" / f"x{uuid.uuid4().hex}"
  domain_path = domain_dir.relative_to(ROOT_DIR).as_posix()
  action_dir = domain_dir / "test_action"

  # Pre-create some files to test early returns
  action_dir.mkdir(parents=True, exist_ok=True)
  (action_dir / "logic.py").write_text("# existing logic")

  test_dir = ROOT_DIR / "tests" / domain_path / "test_action"
  test_dir.mkdir(parents=True, exist_ok=True)
  (test_dir / "test_logic.py").write_text("# existing test")

  req = CreateActionRequest(action_name="Test Action", domain_path=domain_path)
  resp = handle(req)
  assert not resp.errors, f"Unexpected errors: {resp.errors}"


def test_create_action_fails_with_invalid_domain_path():
  req = CreateActionRequest(action_name="Test Action", domain_path="invalid/path/not/under/mhs")
  resp = handle(req)
  assert resp.errors, "Expected error with invalid domain path"


@pytest.mark.integration
def test_create_action_succeeds_with_valid_input():
  """Test that a new action can be created successfully with valid input."""
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
