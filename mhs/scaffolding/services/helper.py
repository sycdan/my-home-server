import os
from pathlib import Path

from mhs.config import ROOT_DIR, TESTS_DIR


class HelperService:
  def ensure_init_files(self, code_dir: Path):
    """Ensure __init__.py files exist in all directories under code_dir."""
    for root, dirs, _ in os.walk(code_dir):
      for dir_name in dirs:
        init_file = Path(root) / dir_name / "__init__.py"
        init_file.touch(exist_ok=True)

  def make_logic_stubs(
    self,
  ):
    """Create logic file stubs if they don't exist."""
    logic_test_dir = TESTS_DIR / "mhs"
    for root, dirs, _ in os.walk(ROOT_DIR / "mhs"):
      for dir_name in dirs:
        logic_dir = Path(root) / dir_name
        test_file = logic_test_dir / logic_dir.relative_to(ROOT_DIR / "mhs") / "test_logic.py"
        if not test_file.exists():
          test_file.parent.mkdir(parents=True, exist_ok=True)
          test_file.write_text("# Logic tests will go here")
          print("Created logic test stub:", test_file)
