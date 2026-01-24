import subprocess

from mhs.output import print_error
from mhs.ssh.run.command import RunCommand


def _run_ssh_command(
  host: str,
  command: str,
  user="",
  identity_file="",
) -> tuple[str, bool]:
  """Returns (output, returncode)"""
  hostname = f"{user}@{host}" if user else host
  args = ["ssh", hostname]
  if identity_file:
    args.extend(["-i", identity_file])
  args.extend(["-x", command])
  try:
    result = subprocess.run(
      args,
      capture_output=True,
      text=True,
      check=False,
    )
    if result.returncode:
      return result.stdout or result.stderr, False
    return result.stdout, True
  except Exception as e:
    print_error(f"SSH command failed: {e}")
    return "Unhandled exception", False


def handle(command: RunCommand):
  return _run_ssh_command(host=command.host, command=command.command)
