import os
from pathlib import Path

for x in os.environ.items():
  if x[0].startswith("MHS_"):
    print(f"{x[0]}={x[1]}")
LOCAL_ROOT = Path(os.getenv("MHS_LOCAL_ROOT", Path(__file__).parent.parent))
