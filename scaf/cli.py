import argparse
import sys

from scaf.loader import load_domain_action
from scaf.output import print_error


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
    domain_action = load_domain_action(args.action_path)
    action_comment = domain_action.action_package.__doc__ or "No comment."
    req_class = get_request_class(req_handler)
    req_parser = build_request_parser(req_class)
    req_parser.prog = f"./call {args.action_path}"

    # Show action-specific help if requested
    if args.help:
      req_parser.print_help()
      return

    req_args = req_parser.parse_args(remaining)
    req_obj = build_request_object(req_class, req_args)
    response = req_handler(req_obj)
    print(json.dumps(to_json(response), indent=2))
  except RuntimeError as e:
    print_error(str(e))
    sys.exit(1)
