from mhs.mhs.821ee6fe08f34e318c38b450dc874596.example.actions.do_stuff.messages_pb2 import DoStuffRequest, DoStuffResponse

def handle(msg: DoStuffRequest) -> DoStuffResponse:
  print(f"Handling {msg}")
  return DoStuffResponse()
