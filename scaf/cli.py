import argparse
import dataclasses
import sys

from mhs.config import ROOT_DIR
from scaf.action_package.load.handler import handle as load_domain_action
from scaf.action_package.load.query import LoadQuery
from scaf.output import print_error


def build_parser_from_shape(shape_class: type, description: str):
  parser = argparse.ArgumentParser(description=description)

  for field in dataclasses.fields(shape_class):
    name = field.name
    type_ = field.type
    default = field.default

    if default is dataclasses.MISSING:
      # required positional
      parser.add_argument(name, type=type_)
    else:
      # optional flag or option
      if type_ is bool:
        parser.add_argument(f"--{name}", action="store_true", default=default)
      else:
        parser.add_argument(f"--{name}", type=type_, default=default)

  return parser


def main(argv=None):
  parser = argparse.ArgumentParser(
    description="Execute a domain action.",
    add_help=False,  # We'll handle help manually
  )
  parser.add_argument("action_path", nargs="?", default="", help="Path to the action's directory.")
  parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit.")
  args, remaining = parser.parse_known_args(argv)

  # Show base help if no action_path is provided
  if not args.action_path:
    if args.help:
      parser.print_help()
    else:
      parser.print_usage()
    return

  try:
    domain_action = load_domain_action(LoadQuery(args.action_path))
    action_comment = domain_action.init_module.__doc__ or "No comment."

    shape_class = domain_action.shape_class
    action_parser = build_parser_from_shape(shape_class, description=action_comment)
    action_parser.prog = f"./call {domain_action.action_dir.relative_to(ROOT_DIR).as_posix()}"

    # Show action-specific help if requested
    if args.help:
      action_parser.print_help()
      return

    action_args = action_parser.parse_args(remaining)
    shape_instance = shape_class(**vars(action_args))
    result = domain_action.logic_module.handle(shape_instance)

    req_args = req_parser.parse_args(remaining)
    req_obj = build_request_object(req_class, req_args)
    response = req_handler(req_obj)
    print(json.dumps(to_json(response), indent=2))
  except RuntimeError as e:
    print_error(str(e))
    sys.exit(1)
