"""Create a new action within the My Home Server project."""
from pathlib import Path
from string import Template

from mhs.config import BASE_DOMAIN, PROTO_DIR, ROOT_DIR
from mhs.gen.internal.create_action.v1.contracts_pb2 import (
  CreateActionRequest,
  CreateActionResponse,
)
from mhs.proto import generate_proto
from mhs.util import to_camel_case, to_dot_path, to_snake_case

ACTION_DIR = Path(__file__).parent
TEMPLATES_DIR = ACTION_DIR / "templates"


def ensure_proto_files(proto_dir: Path):
  contracts_file = proto_dir / "contracts.proto"
  contracts_file.parent.mkdir(parents=True, exist_ok=True)
  if contracts_file.exists():
    raise RuntimeError(f"Proto file already exists: {contracts_file.relative_to(ROOT_DIR)}")

  tmpl_path = TEMPLATES_DIR / "contracts.proto.tmpl"
  tmpl = Template(tmpl_path.read_text(encoding="utf-8"))
  package_path = proto_dir.relative_to(PROTO_DIR)
  proto_content = tmpl.substitute(
    action_package=to_dot_path(package_path),
    action_camel=to_camel_case(package_path.name),
  )
  contracts_file.write_text(proto_content.strip() + "\n")
  return [
    contracts_file,
  ]


def create_file(file_path: Path):
  """Example:
  ```
  if create_file(some_path):
    print("created new file")
  else:
    print("file already existed")
  ```
  """
  if not file_path.exists():
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("")
    return True
  return False


def ensure_logic_module(action_dir: Path):
  logic_module = action_dir / "logic.py"
  if not create_file(logic_module):
    return

  tpl_path = TEMPLATES_DIR / "logic.py.tmpl"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  action_path = action_dir.relative_to(ROOT_DIR)
  content = tpl.substitute(
    action_package=to_dot_path(action_path),
    action_camel=to_camel_case(action_path.name),
  )
  logic_module.write_text(content)


def ensure_test_module(action_dir: Path):
  """Create test file for the action in the tests directory."""
  action_path = action_dir.relative_to(ROOT_DIR)
  test_dir = ROOT_DIR / "tests" / action_path
  test_file = test_dir / "test_logic.py"
  if not create_file(test_file):
    return

  tpl_path = TEMPLATES_DIR / "test_logic.py.tmpl"
  tpl = Template(tpl_path.read_text(encoding="utf-8"))
  content = tpl.substitute(
    action_package=to_dot_path(action_path),
    action_camel=to_camel_case(action_path.name),
    action_snake=to_snake_case(action_path.name),
  )
  test_file.write_text(content)

  # Create __init__.py files  as needed
  create_file(test_dir / "__init__.py")
  parent_dir = test_dir.parent
  while parent_dir != ROOT_DIR / "tests":
    create_file(parent_dir / "__init__.py")
    parent_dir = parent_dir.parent


def handle(msg: CreateActionRequest):
  errors = []
  try:
    domain_path = Path(msg.domain_path.strip())  # must start with base domain
    domain_dir = ROOT_DIR / BASE_DOMAIN / domain_path.relative_to(BASE_DOMAIN)
    domain_dir.mkdir(parents=True, exist_ok=True)
    action_name = msg.action_name.strip()
    action_snake = to_snake_case(action_name)
    action_dir = domain_dir / action_snake
    create_file(action_dir / "__init__.py")
    action_path = action_dir.relative_to(ROOT_DIR)
    ensure_logic_module(action_dir)
    ensure_test_module(action_dir)
    proto_dir = PROTO_DIR / action_path
    generate_proto(ensure_proto_files(proto_dir))
  except Exception as e:
    errors.append(str(e))
  if errors:
    return CreateActionResponse(errors=errors)
  print(f"Created action {action_dir.relative_to(ROOT_DIR)}")
  return CreateActionResponse()
