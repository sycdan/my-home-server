import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Colors for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_info(msg: str) -> None:
  """Print status message in blue"""
  print(f"{BLUE}► {NC} {msg}")


def print_success(msg: str) -> None:
  """Print success message in green"""
  print(f"{GREEN}✓ {NC} {msg}")


def print_warning(msg: str) -> None:
  """Print warning message in yellow to stderr"""
  print(f"{YELLOW}⚠ {NC} {msg}", file=sys.stderr)


def print_error(msg: str) -> None:
  """Print error message in red to stderr"""
  print(f"{RED}✗ {NC} {msg}", file=sys.stderr)
