import re
from pathlib import Path
from string import Template

from mhs import proto
from mhs.actions.create_action.messages_pb2 import CreateActionRequest, CreateActionResponse
from mhs.config import BASE_DOMAIN, ROOT_DIR

ACTION_DIR = Path(__file__).parent
TEMPLATES_DIR = ACTION_DIR / "templates"


def to_snake_case(name):
  return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def to_camel_case(name):
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", name) if word)


def to_dotpath(path: Path):
  return ".".join(path.as_posix().split("/"))


def ensure_proto_files(proto_dir: Path):
  messages_file = proto_dir / "messages.proto"
  messages_file.parent.mkdir(parents=True, exist_ok=True)
  if messages_file.exists():
    raise RuntimeError(f"Proto file already exists: {messages_file.relative_to(ROOT_DIR)}")

  tmpl_path = TEMPLATES_DIR / "messages.proto.tmpl"
  tmpl = Template(tmpl_path.read_text(encoding="utf-8"))
  action_snake = proto_dir.name
  proto_content = tmpl.substitute(
    package_dotpath=to_dotpath(domain_path / "actions" / action_snake),
    action_name_camel=to_camel_case(action_snake),
  )
  messages_file.write_text(proto_content.strip() + "\n")
  return [
    messages_file,
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
    action_name_camel=to_camel_case(action_path.name),
    package_dotpath=to_dotpath(action_path),
  )
  logic_module.write_text(content)


def handle(msg: CreateActionRequest):
  errors = []
  proto_files: list[str] = []
  try:
    domain_path = Path(msg.domain_path.strip())  # must start with base domain
    domain_dir = ROOT_DIR / BASE_DOMAIN / domain_path.relative_to(BASE_DOMAIN)
    domain_dir.mkdir(parents=True, exist_ok=True)
    action_name = msg.action_name.strip()
    action_snake = to_snake_case(action_name)
    action_dir = domain_dir / "actions" / action_snake
    create_file(action_dir / "__init__.py")
    action_path = action_dir.relative_to(ROOT_DIR)
    proto_dir = ROOT_DIR / "proto" / action_path
    proto_files.extend([x.relative_to(ROOT_DIR).as_posix() for x in ensure_proto_files(proto_dir)])
    ensure_logic_module(action_dir)
  except Exception as e:
    errors.append(str(e))
  if errors:
    return CreateActionResponse(success=False, errors=errors)
  print(f"Created action {action_dir.relative_to(ROOT_DIR)}")
  return CreateActionResponse(success=True, proto_files=proto_files)
