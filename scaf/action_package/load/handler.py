import importlib.util
import inspect
import json
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import FunctionType, ModuleType

from mhs.config import ROOT_DIR
from scaf.action_package.entity import ActionPackage
from scaf.action_package.load.query import LoadQuery
from scaf.action_package.rules import must_contain_required_files
from scaf.output import print_error
from scaf.tools import compute_hash, ensure_init_files


def load_handler_module(action_dir: Path) -> ModuleType:
  handler_file = action_dir / "handler.py"
  if not handler_file.exists():
    raise RuntimeError(f"No handler.py file found in {action_dir}.")

  if not handler_file.is_file():
    raise RuntimeError(f"Handler path is not a file: {handler_file}")

  spec = importlib.util.spec_from_file_location("handler_module", str(handler_file))
  if not spec or not spec.loader:
    raise RuntimeError(f"Could not load handler module from {handler_file}")

  handler_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(handler_module)
  return handler_module


def get_handler_name(action_file: Path) -> str:
  return f"handle_{action_file.parent.name}"


def get_handler(handler_name: str, action_module: ModuleType) -> FunctionType:
  handler = getattr(action_module, handler_name, None)
  if handler is None:
    raise RuntimeError(f"{action_module.__file__} does not define an '{handler_name}' function.")
  return handler


def get_action_class(handler: FunctionType) -> type:
  action_file: Path = Path()
  sig = inspect.signature(handler)
  params = list(sig.parameters.values())
  if len(params) != 1:
    raise RuntimeError("Handler function must take a single parameter.")

  #  and params[0].annotation != inspect.Parameter.empty
  #   request_class = params[0].annotation
  #   if issubclass(request_class, Message):
  #     return request_class


###### new scaf stuff ######


def resolve_path(action_path: Path | str) -> Path:
  if isinstance(action_path, str):
    action_path = Path(action_path)
  return action_path.resolve()


def _load_module_from_file(file: Path, hash: str = "") -> ModuleType:
  if file.is_dir():
    file = file / "__init__.py"

  if not file.exists():
    raise RuntimeError(f"Module file does not exist: {file}")

  hash = hash or compute_hash(file)
  module_name = f"module_{hash}"
  spec = importlib.util.spec_from_file_location(module_name, str(file))
  if not spec or not spec.loader:
    raise RuntimeError(f"Could not load module from {file}")

  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def ensure_action_dir(action_path: Path | str) -> Path:
  if isinstance(action_path, str):
    action_path = Path(action_path)
  action_path = action_path.resolve()
  if not action_path.exists():
    raise RuntimeError(f"Action path does not exist: {action_path.relative_to(ROOT_DIR)}.")
  action_dir = action_path if action_path.is_dir() else action_path.parent
  return action_dir


def load_init_module(action_dir: Path, action_hash: str) -> ModuleType:
  return _load_module_from_file(action_dir / "__init__.py", action_hash)


def load_shape_module(action_dir: Path) -> ModuleType:
  try:
    return _load_module_from_file(action_dir / "command.py")
  except Exception:
    return _load_module_from_file(action_dir / "query.py")


def load_logic_module(action_dir: Path) -> ModuleType:
  return _load_module_from_file(action_dir / "handler.py")


def extract_first_class(module) -> type:
  for name, obj in vars(module).items():
    if isinstance(obj, type) and not name.startswith("_"):
      return obj
  raise RuntimeError(f"No class found in {module.__file__}")


def handle(query: LoadQuery) -> ActionPackage:
  action_dir = ensure_action_dir(query.action_path)
  must_contain_required_files(filenames=[f.name for f in action_dir.iterdir()])
  action_hash = compute_hash(action_dir)
  init_module = load_init_module(action_dir, action_hash)
  shape_module = load_shape_module(action_dir)
  logic_module = load_logic_module(action_dir)
  shape_class = extract_first_class(shape_module)
  return ActionPackage(
    action_dir=action_dir,
    action_hash=action_hash,
    init_module=init_module,
    shape_module=shape_module,
    logic_module=logic_module,
    shape_class=shape_class,
  )
