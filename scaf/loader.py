import importlib.util
import inspect
import json
import sys
import uuid
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import FunctionType, ModuleType

from mhs.config import ROOT_DIR
from scaf.action_package.entity import ActionPackage
from scaf.action_package.rules import must_contain_required_files
from scaf.output import print_error
from scaf.tools import ensure_init_files


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


def locate_action_file(action_path: Path | str) -> Path:
  """returns the path to the action's command.py or query.py file."""
  action_path = resolve_path(action_path)
  if not action_path.exists():
    raise RuntimeError(f"Action path does not exist: {action_path}")

  if action_path.is_file() and action_path.name in {"command.py", "query.py"}:
    return action_path

  if action_path.is_dir():
    command_file = action_path / "command.py"
    query_file = action_path / "query.py"

    if command_file.exists() and query_file.exists():
      raise RuntimeError(
        f"Either command.py or query.py may exist in {action_path}, but not both."
      )

    if command_file.exists():
      return command_file

    if query_file.exists():
      return query_file

  raise RuntimeError(f"No command.py or query.py. file found at {action_path}.")


def _load_module_from_file(file: Path, hash: str = "") -> ModuleType:
  if file.is_dir():
    file = file / "__init__.py"

  if not file.exists():
    raise RuntimeError(f"Module file does not exist: {file}")

  hash = hash or sha256(file.as_posix().encode("utf-8")).hexdigest()
  module_name = f"module_{hash}"
  spec = importlib.util.spec_from_file_location(module_name, str(file))
  if not spec or not spec.loader:
    raise RuntimeError(f"Could not load module from {file}")

  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def _get_handler_function(logic_module: ModuleType) -> FunctionType:
  pass


def _ensure_action_dir(action_path: Path | str) -> Path:
  if isinstance(action_path, str):
    action_path = Path(action_path)
  action_path = action_path.resolve()
  if not action_path.exists():
    raise RuntimeError(f"Action path does not exist: {action_path.relative_to(ROOT_DIR)}.")
  action_dir = action_path if action_path.is_dir() else action_path.parent
  return action_dir


def load_domain_action(action_path: Path | str) -> ActionPackage:
  action_dir = _ensure_action_dir(action_path)
  must_contain_required_files([f.name for f in action_dir.iterdir()])

  handler_module = load_handler_module(action_path)
  action_file = locate_action_file(action_path)
  action_dir = action_file.parent
  action_hash = sha256(action_dir.as_posix().encode("utf-8")).hexdigest()
  ensure_init_files(action_dir)
  action_package = _load_module_from_file(action_dir / "__init__.py", action_hash)
  action_module = _load_module_from_file(action_file)
  handler = get_handler_function(logic_module)
  return DomainActionPackage(
    action_hash=action_hash,
    action_dir=action_dir,
    action_package=action_package,
    action_file=action_file,
    action_module=action_module,
  )
