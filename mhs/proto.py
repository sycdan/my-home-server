import json
import subprocess

from google.protobuf import json_format, text_format

from mhs.config import FLEET_FILE, ROOT_DIR


def generate_proto():
  """Generate Python code from the fleet.proto schema."""
  result = subprocess.run(
    [
      "c:/protoc/bin/protoc",
      "-I=proto",
      "--python_out=.",
      "--pyi_out=.",
      "proto/mhs/config/fleet.proto",
    ],
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    raise RuntimeError(f"protoc failed: {result.stderr}")


def generate_fleet_json():
  generate_proto()
  from mhs.config import fleet_pb2

  with open("mhs/config/fleet.textproto", "r") as f:
    text = f.read()
  proto_obj = fleet_pb2.Fleet()
  text_format.Parse(text, proto_obj)
  generated = json_format.MessageToDict(proto_obj, preserving_proto_field_name=True)
  with open(FLEET_FILE, "w") as f:
    json.dump(generated, f, indent=2)
