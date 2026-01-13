import os
import shutil
import subprocess
from pathlib import Path

from mhs.config import PROTO_DIR, PROTOC_PATH, ROOT_DIR


def find_proto_files():
  """Find all .proto files in the proto/ directory."""
  proto_files: list[Path] = []
  for root, _, files in os.walk(ROOT_DIR / "proto"):
    for file in files:
      if file.endswith(".proto"):
        proto_files.append(Path(root) / file)
  return proto_files


def generate_proto(files: list[Path] | None = None, output_path="."):
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
    files = find_proto_files()
  args.extend([x.relative_to(ROOT_DIR).as_posix() for x in files])
  result = subprocess.run(args, capture_output=True, text=True, cwd=ROOT_DIR)
  if result.returncode != 0:
    raise RuntimeError(f"Failed while compiling proto files: {result.stderr}")

  # Walk the output dir and create __init__.py files
  for root, dirs, _ in os.walk(output_dir):
    for dir_name in dirs:
      init_file = Path(root) / dir_name / "__init__.py"
      init_file.touch(exist_ok=True)
