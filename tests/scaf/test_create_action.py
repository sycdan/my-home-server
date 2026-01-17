import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from mhs.config import BASE_DOMAIN, ROOT_DIR
from scaf import cli


@pytest.fixture(autouse=True)
def cleanup_example_dirs():
  """Automatically clean up any leftover example directories after each test."""
  yield  # Run the test
  # Cleanup after test regardless of success/failure
  for pattern in ["mhs/example/x*", "proto/mhs/example/x*", "tests/mhs/example/x*"]:
    for path in ROOT_DIR.glob(pattern):
      if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


@pytest.mark.integration
def test_create_action_does_not_overwrite_existing_files():
  """We'll create an action twice with the same data."""
  new_domain_dir = ROOT_DIR / BASE_DOMAIN / "example" / f"x{uuid.uuid4().hex[:8]}"
  new_action_name = "Do Stuff"
  action_args = [
    "--domain_path",
    new_domain_dir.relative_to(ROOT_DIR).as_posix(),
    "--action_name",
    new_action_name,
    "--comment",
    "Create a new domain action.",
  ]
  cli.main(["scaf/create_action/handler.py"] + action_args)
  # TODO hash it after creation to verify files created
  # TODO create again
  # TODO hash it again to verify no changes
