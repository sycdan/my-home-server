from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DOMAIN = "mhs"
FLEET_FILE = ROOT_DIR / "fleet.json"
EXAMPLE_ENV_FILE = ROOT_DIR / "example.env"
ENV_FILE = ROOT_DIR / ".env"
DOMAIN_SUFFIX = "lan"
