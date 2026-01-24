from mhs.config import FLEET_FILE
from mhs.storage.load_media import handler
from mhs.storage.load_media.query import LoadMediaQuery


def handle():
  media = handler.handle(LoadMediaQuery(FLEET_FILE))
  print(media)
