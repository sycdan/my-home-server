@dataclass
class RuntimeContext:
  action_dir: Path
  action_file: Path | None = field(default=None)
  handler_module: ModuleType | None = field(default=None)
  handler_function: FunctionType | None = field(default=None)