import os
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


def generate_proto(files: list[Path] | None = None):
  """Generate Python code and project structure from the proto schema."""
  args = [
    PROTOC_PATH,
    f"-I={PROTO_DIR.relative_to(ROOT_DIR)}",
    "--python_out=.",
    "--pyi_out=.",
  ]
  if files is None:
    files = find_proto_files()
  args.extend([x.relative_to(ROOT_DIR).as_posix() for x in files])
  result = subprocess.run(args, capture_output=True, text=True, cwd=ROOT_DIR)
  if result.returncode != 0:
    raise RuntimeError(f"Failed while compiling proto files: {result.stderr}")
