from mhs.mhs.ebbef19e9dcb4cc5a501c4ed57061443.example.actions.do_stuff.messages_pb2 import DoStuffRequest, DoStuffResponse

def handle(msg: DoStuffRequest) -> DoStuffResponse:
  print(f"Handling {msg}")
  return DoStuffResponse()
