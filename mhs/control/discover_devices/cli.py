"""
Device discovery initializer.
Generates RouterOS scripts for each device and deploys them to the router.
Loads configuration from .env files.
"""



def set_debug(value: bool) -> None:
  global DEBUG
  DEBUG = value




def main(argv=None):
  parser = argparse.ArgumentParser(description="Deploy device discovery scripts to router.")
  parser.add_argument("device", nargs="?", default=None, help="Specific device to discover.")
  parser.add_argument(
    "--debug",
    action="store_true",
    help="Enable debug output",
  )
  args = parser.parse_args(argv)

  set_debug(args.debug)

  if DEBUG:
    print_info(f"Using config: {CONFIG}")
    print_info(f"Fleet file: {FLEET_FILE}")
