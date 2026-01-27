from mhs.data.fleet.load.query import LoadFleet
from mhs.data.fleet.load_server.query import LoadServer
from mhs.device.server.entity import Server


def handle(query: LoadServer) -> Server:
  fleet = LoadFleet().execute()
  try:
    return fleet.servers[query.ref]
  except KeyError:
    raise RuntimeError(f"Unknown server {query.ref}")
