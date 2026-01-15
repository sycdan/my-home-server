#!/usr/bin/env python
from mhs.config import ROOT_DIR
from mhs.output import print_info, print_success
from mhs.scaffolding import (
  ensure_init_files,
  find_proto_files,
  generate_proto,
  make_api_contract_test_stubs,
  make_logic_stubs,
)

print_info("Finding proto files...")
proto_files = find_proto_files()
print_success(f"Found {len(proto_files)} proto files:")
for file in proto_files:
  print(f" - {file.relative_to(ROOT_DIR)}")
print_info("Compiling proto files...")
generate_proto(proto_files, "gen")
print_success(f"Compiled {len(proto_files)} proto files.")

# make_api_contract_test_stubs()
# make_logic_stubs()

ensure_init_files(ROOT_DIR / "mhs")
ensure_init_files(ROOT_DIR / "gen")
