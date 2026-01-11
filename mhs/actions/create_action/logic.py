from mhs.actions.create_action.messages_pb2 import CreateActionRequest, CreateActionResponse


def handle(msg: CreateActionRequest) -> CreateActionResponse:
  print(f"Creating action '{msg.action_name}' in domain '{msg.domain_path}'")
  # Logic to create the action would go here
  return CreateActionResponse(success=True)
