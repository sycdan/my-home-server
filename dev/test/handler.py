import subprocess
import sys

from dev.test.command import Test


def handle(command: Test):
  result = subprocess.run([sys.executable, "-m", "pytest"], check=True)
  return result.returncode