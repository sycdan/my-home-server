import json
import os
import subprocess
from pathlib import Path

from google.protobuf import json_format, text_format

from mhs.config import FLEET_FILE, PROTOC_PATH, ROOT_DIR

PROTO_DIR = ROOT_DIR / "proto"


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


# def generate_fleet_json():
#   from mhs.config import fleet_pb2

#   with open("mhs/config/fleet.textproto", "r") as f:
#     text = f.read()
#   proto_obj = fleet_pb2.Fleet()
#   text_format.Parse(text, proto_obj)
#   generated = json_format.MessageToDict(proto_obj, preserving_proto_field_name=True)
#   with open(FLEET_FILE, "w") as f:
#     json.dump(generated, f, indent=2)


print(generate_proto())
