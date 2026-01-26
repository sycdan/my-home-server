from mhs.control.run_docker_compose.command import RunDockerCompose
from mhs.ssh.run_on.command import RunOn


def handle(command: RunDockerCompose):
  server = command.server
  args = " ".join(command.args)
  cd_command = f"cd ./{command.remote_dir.as_posix()}"
  dc_command = f"docker compose {args}"
  output, success = RunOn(
    command.server.ssh_host,
    f"{cd_command} && {dc_command}",
  ).execute()
  if not success:
    raise RuntimeError(f"Failed to run {dc_command} on {server}: {output}")
