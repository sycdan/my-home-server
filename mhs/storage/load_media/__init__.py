from mhs.storage.entity import Storage
from mhs.storage.load_media.handler import handle
from mhs.storage.load_media.query import LoadMediaQuery


def call(*args, **kwargs) -> list[Storage] | dict[str, Storage]:
  query = LoadMediaQuery(*args, **kwargs)
  return handle(query)
