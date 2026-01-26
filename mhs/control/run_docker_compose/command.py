from dataclasses import dataclass
from pathlib import Path

from mhs.device.server.entity import Server


@dataclass
class RunDockerCompose:
  server: Server
  remote_dir: Path
  args: list[str]

  def execute(self) -> None:
    from mhs.control.run_docker_compose.handler import handle

    handle(self)
