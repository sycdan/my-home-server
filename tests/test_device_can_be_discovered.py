"""Happy-path test for discovering a real server."""

import pytest

from mhs.control.discover_devices.command import DiscoverDevices
from tests.conftest import Sandbox


@pytest.mark.integration
def test(sandbox: Sandbox):
  DiscoverDevices(skip_dns_refresh=True).execute()
