import importlib.util
import inspect
import json
import sys
import uuid
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import FunctionType, ModuleType

from scaf.errors import ScaffoldingError
from scaf.output import print_error
from scaf.tools import ensure_init_files


@dataclass
class DomainAction:
  action_dir: Path
  action_hash: str
  action_module: ModuleType


def load_action_module(action_path: Path) -> ModuleType:
  action_dir = _locate_action_dir(action_path)
  action_file = locate_action_file(action_dir)
  if not action_file.is_file():
    raise ScaffoldingError(f"Action path is not a file: {action_file}")

  spec = importlib.util.spec_from_file_location("action_module", str(action_file))
  if not spec or not spec.loader:
    raise ScaffoldingError(f"Could not load action module from {action_file}")

  action_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(action_module)
  return action_module


def locate_action_file(action_dir: Path) -> Path:
  command_file = action_dir / "command.py"
  query_file = action_dir / "query.py"

  if command_file.exists() and query_file.exists():
    raise ScaffoldingError(
      f"Either command.py or query.py may exist in {action_dir}, but not both."
    )

  if command_file.exists():
    return command_file

  if query_file.exists():
    return query_file

  raise ScaffoldingError(
    f"No action file found in {action_dir}. Create either command.py or query.py."
  )


def load_handler_module(action_dir: Path) -> ModuleType:
  handler_file = action_dir / "handler.py"
  if not handler_file.exists():
    raise ScaffoldingError(f"No handler.py file found in {action_dir}.")

  if not handler_file.is_file():
    raise ScaffoldingError(f"Handler path is not a file: {handler_file}")

  spec = importlib.util.spec_from_file_location("handler_module", str(handler_file))
  if not spec or not spec.loader:
    raise ScaffoldingError(f"Could not load handler module from {handler_file}")

  handler_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(handler_module)
  return handler_module


def get_handler_name(action_file: Path) -> str:
  return f"handle_{action_file.parent.name}"


def get_handler(handler_name: str, action_module: ModuleType) -> FunctionType:
  handler = getattr(action_module, handler_name, None)
  if handler is None:
    raise ScaffoldingError(
      f"{action_module.__file__} does not define an '{handler_name}' function."
    )
  return handler


def get_action_class(handler: FunctionType) -> type:
  action_file: Path = Path()
  sig = inspect.signature(handler)
  params = list(sig.parameters.values())
  if len(params) != 1:
    raise ScaffoldingError("Handler function must take a single parameter.")

  #  and params[0].annotation != inspect.Parameter.empty
  #   request_class = params[0].annotation
  #   if issubclass(request_class, Message):
  #     return request_class


###### 2026-01-16 new stuff below here ######


def _locate_action_dir(action_path: Path | str) -> Path:
  if not isinstance(action_path, Path):
    action_path = Path(action_path)

  if not action_path.is_absolute():
    action_path = action_path.resolve()

  if not action_path.exists():
    raise ScaffoldingError(f"Action path does not exist: {action_path}")

  if action_path.is_dir():
    return action_path
  elif action_path.is_file() and action_path.name in ("command.py", "query.py"):
    return action_path.parent

  raise ScaffoldingError(
    f"Invalid action path: {action_path}. Must be a directory or command.py/query.py file."
  )


def _load_action_module(action_dir: Path, action_hash: str) -> ModuleType:
  if not action_dir.exists():
    raise ScaffoldingError(f"Action directory does not exist: {action_dir}")

  if not action_dir.is_dir():
    raise ScaffoldingError(f"Action path is not a directory: {action_dir}")

  init_file = action_dir / "__init__.py"
  if not init_file.exists():
    raise ScaffoldingError(
      f"Action directory is not a package (missing __init__.py): {action_dir}"
    )

  spec = importlib.util.spec_from_file_location(f"action_{action_hash}", str(init_file))
  if not spec or not spec.loader:
    raise ScaffoldingError(f"Action directory is not loadable: {action_dir}")

  action_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(action_module)
  return action_module


def load_domain_action(action_path: Path | str) -> DomainAction:
  action_dir = _locate_action_dir(action_path)
  action_hash = sha256(action_dir.as_posix().encode("utf-8")).hexdigest()
  ensure_init_files(action_dir)
  action_module = _load_action_module(action_dir, action_hash)
  return DomainAction(
    action_dir=action_dir,
    action_hash=action_hash,
    action_module=action_module,
  )
