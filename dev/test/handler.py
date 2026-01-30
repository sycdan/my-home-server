import subprocess

from dev.test.command import Test


def handle(command: Test):
  result = subprocess.run(["pytest"], check=True)
  return result.returncode