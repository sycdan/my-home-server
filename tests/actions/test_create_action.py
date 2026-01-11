import shutil
import uuid

from mhs.actions.create_action.logic import CreateActionRequest, handle
from mhs.config import BASE_DOMAIN, ROOT_DIR
from mhs.proto import generate_proto


def test_create_action_basic():
  """Test that a new action can be created with minimal input."""
  domain_dir = ROOT_DIR / BASE_DOMAIN / "examples" / uuid.uuid4().hex
  assert not domain_dir.exists()

  domain_path = domain_dir.relative_to(ROOT_DIR).as_posix()
  req = CreateActionRequest(action_name="Do Stuff", domain_path=domain_path)
  resp = handle(req)
  assert resp.success

  generate_proto([ROOT_DIR / x for x in resp.proto_files])

  # Verify expected structure and files
  py_dir = domain_dir / "actions" / "do_stuff"
  proto_dir = ROOT_DIR / "proto" / domain_path / "actions" / "do_stuff"
  assert py_dir.is_dir(), f"Missing {py_dir}"
  assert proto_dir.is_dir(), f"Missing {proto_dir}"
  assert (py_dir / "__init__.py").is_file(), "Missing __init__.py"
  assert (py_dir / "logic.py").is_file(), "Missing logic.py"
  assert (proto_dir / "messages.proto").is_file(), "Missing messages.proto"

  # Clean up
  shutil.rmtree(domain_dir, ignore_errors=True)
  shutil.rmtree(proto_dir, ignore_errors=True)
