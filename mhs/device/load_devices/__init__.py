from mhs.device.load_devices.handler import handle
from mhs.device.load_devices.query import LoadDevicesQuery


def index(*args, **kwargs):
  query = LoadDevicesQuery(*args, **kwargs)
  records = handle(query)
  return {record.key: record for record in records}
