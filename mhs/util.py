import re
from pathlib import Path


def to_snake_case(name):
  return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def to_camel_case(name):
  return "".join(word.capitalize() for word in re.split(r"[^a-zA-Z0-9]", name) if word)


def to_dotpath(path: Path):
  return ".".join(path.as_posix().split("/"))
