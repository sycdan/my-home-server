from dataclasses import dataclass, field


@dataclass
class ExecuteServiceScript:
  """Executes a service script on its host."""

  executable: str = field(
    metadata={"help": "Relative path to executable script from root"},
  )

  def execute(self, *args, **kwargs):
    from mhs.control.execute_service_script.handler import handle

    return handle(self, *args, **kwargs)
