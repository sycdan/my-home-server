from mhs.data.fleet.load.query import LoadFleet
from mhs.data.fleet.load_service.query import LoadService
from mhs.service.entity import Service


def handle(query: LoadService) -> Service:
  fleet = LoadFleet().execute()
  try:
    return fleet.services[query.ref]
  except KeyError:
    raise RuntimeError(f"Unknown service {query.ref}")
