from dataclasses import dataclass, field


@dataclass
class ExecuteServiceScript:
  """Executes a service script on its host."""

  executable: str = field(
    metadata={"help": "Relative path to executable script from root"},
  )
  script_args: list[str] = field(
    default_factory=list,
    metadata={"help": "Arguments to pass to the script"},
  )

  def execute(self):
    from mhs.control.execute_service_script.handler import handle

    return handle(self)
