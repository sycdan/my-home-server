import re
import textwrap
from pathlib import Path

from mhs.actions.create_action.messages_pb2 import CreateActionRequest, CreateActionResponse
from mhs.config import BASE_DOMAIN, ROOT_DIR


def to_snake_case(name):
  return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def to_camel_case(name):
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", name) if word)


def handle(msg: CreateActionRequest) -> CreateActionResponse:
  errors = []
  try:
    domain_path = Path(msg.domain_path.strip())
    domain_dir = ROOT_DIR / BASE_DOMAIN / domain_path.relative_to(BASE_DOMAIN)
    action_name = msg.action_name.strip()
    action_dir = domain_dir / "actions" / to_snake_case(action_name)
    action_path = action_dir.relative_to(ROOT_DIR)
    proto_dir = ROOT_DIR / "proto" / action_path

    domain_dir.parent.mkdir(parents=True, exist_ok=True)
    proto_dir.parent.mkdir(parents=True, exist_ok=True)

    proto_name = to_camel_case(action_name)
    proto_file = proto_dir / "messages.proto"
    if proto_file.exists():
      raise RuntimeError(f"Proto file already exists: {proto_file.relative_to(ROOT_DIR)}")

    proto_content = (
      textwrap.dedent(f"""
      edition = "2024";
      package mhs.{domain_path_str.replace("/", ".")}.actions.{to_snake_case(action_name)};

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
        from mhs.{domain_path_str.replace("/", ".")}.actions.{to_snake_case(action_name)}.messages_pb2 import {proto_name}Request, {proto_name}Response

        def handle(msg: {proto_name}Request) -> {proto_name}Response:
          print(f"Handling {{msg}}")
          return {proto_name}Response()
      """).strip()
        + "\n"
      )
      logic_file.write_text(logic_content)
  except Exception as e:
    errors.append(str(e))

  if errors:
    return CreateActionResponse(success=False, errors=errors)
  print(f"Created action {action_dir.relative_to(ROOT_DIR)}")
  return CreateActionResponse(success=True, errors=[])
