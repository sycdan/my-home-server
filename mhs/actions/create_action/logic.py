import os
import re
import textwrap
from pathlib import Path

from mhs.actions.create_action.messages_pb2 import CreateActionRequest, CreateActionResponse


def handle(msg: CreateActionRequest) -> CreateActionResponse:
  # Normalize action and domain
  action_name = msg.action_name.strip()
  domain_path = msg.domain_path.strip().replace("\\", "/")
  # Require domain_path to start with 'mhs/' and be relative
  if not domain_path.startswith("mhs/"):
    raise ValueError("domain_path must start with 'mhs/' and be a relative path from the root directory")

  # Convert action name to snake_case for directory, CamelCase for proto
  def to_snake_case(name):
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()

  def to_camel_case(name):
    return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", name) if word)

  # Ensure domain path exists for both proto and python
  action_dir = Path(f"mhs/{domain_path}/actions/{to_snake_case(action_name)}")
  proto_dir = Path(f"proto/mhs/{domain_path}/actions/{to_snake_case(action_name)}")
  action_dir.parent.mkdir(parents=True, exist_ok=True)
  proto_dir.parent.mkdir(parents=True, exist_ok=True)
  action_dir.mkdir(parents=True, exist_ok=True)
  proto_dir.mkdir(parents=True, exist_ok=True)

  # Proto file
  proto_name = to_camel_case(action_name)
  proto_file = proto_dir / "messages.proto"
  if not proto_file.exists():
    proto_content = (
      textwrap.dedent(f"""
      edition = "2024";
      package mhs.{domain_path.replace("/", ".")}.actions.{to_snake_case(action_name)};

      message {proto_name}Request {{

      }}

      message {proto_name}Response {{
      }}
    """).strip()
      + "\n"
    )
    proto_file.write_text(proto_content)

  # Python package __init__.py
  init_file = action_dir / "__init__.py"
  if not init_file.exists():
    init_file.write_text("")

  # logic.py
  logic_file = action_dir / "logic.py"
  if not logic_file.exists():
    logic_content = (
      textwrap.dedent(f"""
      from mhs.{domain_path.replace("/", ".")}.actions.{to_snake_case(action_name)}.messages_pb2 import {proto_name}Request, {proto_name}Response

      def handle(msg: {proto_name}Request) -> {proto_name}Response:
        print(f"Handling {{msg}}")
        return {proto_name}Response()
    """).strip()
      + "\n"
    )
    logic_file.write_text(logic_content)

  print(f"Created action '{action_name}' in domain '{msg.domain_path}'")
  return CreateActionResponse(success=True)
