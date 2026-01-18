def validate_mac_address(mac: str) -> bool:
  """Validate MAC address format"""
  if len(mac.split(":")) != 6:
    return False
  for part in mac.split(":"):
    if len(part) != 2:
      return False
    try:
      int(part, 16)
    except ValueError:
      return False
  return True
