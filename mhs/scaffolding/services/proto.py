import os
import shutil
import subprocess
from pathlib import Path

from mhs.config import PROTO_DIR, PROTOC_PATH, ROOT_DIR, TESTS_DIR


class ProtoService:
  def find_proto_files(self):
    """Find all .proto files in the proto/ directory."""
    proto_files: list[Path] = []
    for root, _, files in os.walk(ROOT_DIR / "proto"):
      for file in files:
        if file.endswith(".proto"):
          proto_files.append(Path(root) / file)
    return proto_files

  def generate_proto(self, files: list[Path] | None = None, output_path="."):
    """Generate Python code and project structure from the proto schema."""
    output_dir = (ROOT_DIR / output_path).resolve()
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    args = [
      PROTOC_PATH,
      f"-I={PROTO_DIR.relative_to(ROOT_DIR)}",
      f"--python_out={output_dir.relative_to(ROOT_DIR).as_posix()}",
      f"--pyi_out={output_dir.relative_to(ROOT_DIR).as_posix()}",
    ]
    if files is None:
      files = self.find_proto_files()
    args.extend([x.relative_to(ROOT_DIR).as_posix() for x in files])
    result = subprocess.run(args, capture_output=True, text=True, cwd=ROOT_DIR)
    if result.returncode != 0:
      raise RuntimeError(f"Failed while compiling proto files: {result.stderr}")

    # Walk the output dir and create __init__.py files
    for root, dirs, _ in os.walk(output_dir):
      for dir_name in dirs:
        init_file = Path(root) / dir_name / "__init__.py"
        init_file.touch(exist_ok=True)

  def make_api_contract_test_stubs(self, proto_files: list[Path] | None = None):
    """Create test stubs proto files."""
    if proto_files is None:
      proto_files = self.find_proto_files()

    for file in proto_files:
      rel_path = file.relative_to(PROTO_DIR).with_suffix("")
      print(rel_path)

      if file.stem == "contracts":
        golden_test_file = TESTS_DIR / "api" / rel_path.parent / f"test_{file.stem}.py"
        if not golden_test_file.exists():
          golden_test_file.parent.mkdir(parents=True, exist_ok=True)
          golden_test_file.write_text("# Golden tests will go here")
          print("Created golden test stub:", golden_test_file)

        integration_test_file = TESTS_DIR / "api" / rel_path.parent / "test_surface.py"
        if not integration_test_file.exists():
          integration_test_file.parent.mkdir(parents=True, exist_ok=True)
          integration_test_file.write_text("# Integration tests will go here")
          print("Created integration test stub:", integration_test_file)

  def ensure_init_files(self, code_dir: Path):
    """Ensure __init__.py files exist in all directories under code_dir."""
    for root, dirs, _ in os.walk(code_dir):
      for dir_name in dirs:
        init_file = Path(root) / dir_name / "__init__.py"
        init_file.touch(exist_ok=True)

  def make_logic_stubs(self, ):
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
