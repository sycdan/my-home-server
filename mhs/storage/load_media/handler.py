import json

from mhs.storage.entity import Storage
from mhs.storage.load_media.query import LoadMediaQuery


def handle(query: LoadMediaQuery) -> list[Storage]:
  storages: list[Storage] = []
  fleet = json.loads(query.fleet_file.read_text())
  data = fleet.get(query.data_key, {})
  for key, vars in data.items():
    storages.append(Storage(key, **vars))
  return storages
