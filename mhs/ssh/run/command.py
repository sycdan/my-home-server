from dataclasses import dataclass


@dataclass
class RunCommand:
  host: str
  command: str

  def execute(self):
    from mhs.ssh.run.handler import handle

    return handle(self)
