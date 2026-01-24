from mhs.storage.load_media.handler import handle
from mhs.storage.load_media.query import LoadMediaQuery


def index(*args, **kwargs):
  query = LoadMediaQuery(*args, **kwargs)
  records = handle(query)
  return {record.key: record for record in records}
