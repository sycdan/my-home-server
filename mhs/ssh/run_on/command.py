from dataclasses import dataclass


@dataclass
class RunOn:
  ssh_host: str
  command: str

  def execute(self):
    from mhs.ssh.run_on.handler import handle

    return handle(self)
