import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mhs.run.logic import RunRequest, handle, validate_executable

TEST_SERVICE_LABEL = "testing"
TEST_FLEET_JSON = """
{
	"devices": {
		"r-pi": {
			"description": "Raspberry Pi 3",
			"ssh_host": "ingress",
			"macs": ["B8:27:EB:AB:C0:DC"],
			"services": {
				"<<service-label>>": {
					"port": 59999
				}
			}
		}
	}
}
""".strip().replace("<<service-label>>", TEST_SERVICE_LABEL)


def test_validate_executable_fails_when_file_does_not_exist():
  """Test that validate_executable exits with error when target file does not exist."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    with pytest.raises(SystemExit):
      validate_executable("/non/existent/file", root_dir)


def test_validate_executable_fails_when_path_is_directory():
  """Test that validate_executable exits with error when path points to directory instead of file."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    dir_path = root_dir / "services" / "test"
    dir_path.mkdir(parents=True)
    
    with pytest.raises(SystemExit):
      validate_executable(str(dir_path), root_dir)


def test_validate_executable_fails_when_file_outside_project():
  """Test that validate_executable exits with error when executable is outside project directory."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    # Create a file outside the root directory
    outside_file = Path(temp_dir).parent / "outside_file"
    outside_file.write_text("#!/bin/bash\necho test")
    
    try:
      with pytest.raises(SystemExit):
        validate_executable(str(outside_file), root_dir)
    finally:
      outside_file.unlink(missing_ok=True)


def test_validate_executable_fails_when_not_in_services_directory():
  """Test that validate_executable exits with error when executable is not in services directory structure."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    wrong_file = root_dir / "wrong" / "location" / "script"
    wrong_file.parent.mkdir(parents=True)
    wrong_file.write_text("#!/bin/bash\necho test")
    
    with pytest.raises(SystemExit):
      validate_executable(str(wrong_file), root_dir)


@patch('os.access')
def test_validate_executable_warns_when_file_not_executable(mock_access):
  """Test that validate_executable warns but succeeds when file is not marked executable."""
  mock_access.return_value = False  # Mock non-executable file
  
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    service_dir = root_dir / "services" / "test"
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    
    with patch("mhs.run.logic.print_warning") as mock_warn:
      result = validate_executable(str(script_file), root_dir)
      assert result == Path("services/test/init")
      mock_warn.assert_called_once()


def test_validate_executable_succeeds_with_valid_executable():
  """Test that validate_executable returns correct relative path for valid executable in services directory."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    service_dir = root_dir / "services" / "test"
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    result = validate_executable(str(script_file), root_dir)
    assert result == Path("services/test/init")


@patch('mhs.run.logic.Device.load_all')
def test_handle_fails_when_service_not_found_in_fleet(mock_load_all):
  """Test that handle fails with descriptive error when service is not configured in fleet.json."""
  # Mock empty device list
  mock_load_all.return_value = []
  
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    
    # Create fleet file 
    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text('{"devices": {}}')
    
    # Create service directory and executable
    service_dir = root_dir / "services" / "unknown"
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    request = RunRequest(
      executable_path=str(script_file),
      root_directory=str(root_dir),
      debug=False
    )
    
    response = handle(request)
    assert response.errors
    assert "is not hosted on any device" in response.errors[0]


@patch("mhs.run.logic.bidirectional_sync")
def test_handle_fails_when_file_synchronization_fails(mock_sync):
  """Test that handle fails with descriptive error when file synchronization to remote host fails."""
  mock_sync.return_value = False
  
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    
    # Create fleet file with service
    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text(TEST_FLEET_JSON)
    
    # Create service directory and executable
    service_dir = root_dir / "services" / TEST_SERVICE_LABEL
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    request = RunRequest(
      executable_path=str(script_file),
      root_directory=str(root_dir),
      debug=False
    )
    
    response = handle(request)
    assert response.errors
    assert "File synchronization failed" in response.errors[0]


@patch("mhs.run.logic.subprocess.run")
@patch("mhs.run.logic.bidirectional_sync")
def test_handle_fails_when_remote_execution_fails(mock_sync, mock_run):
  """Test that handle fails with descriptive error when remote command execution fails."""
  mock_sync.return_value = True
  
  # Mock failed subprocess execution
  mock_result = Mock()
  mock_result.returncode = 1
  mock_result.stderr = "Command failed"
  mock_result.stdout = ""
  mock_run.return_value = mock_result
  
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    
    # Create fleet file with service
    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text(TEST_FLEET_JSON)
    
    # Create service directory and executable
    service_dir = root_dir / "services" / TEST_SERVICE_LABEL
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    request = RunRequest(
      executable_path=str(script_file),
      root_directory=str(root_dir),
      debug=False
    )
    
    response = handle(request)
    assert response.errors
    assert "Remote execution failed" in response.errors[0]


@patch("mhs.run.logic.subprocess.run")
@patch("mhs.run.logic.bidirectional_sync")
@patch("mhs.run.logic.ensure_remote_dir")
def test_handle_succeeds_with_debug_output(mock_ensure_dir, mock_sync, mock_run):
  """Test that handle succeeds and provides detailed debug output when debug mode is enabled."""
  mock_sync.return_value = True
  
  # Mock successful subprocess execution
  mock_result = Mock()
  mock_result.returncode = 0
  mock_result.stderr = ""
  mock_result.stdout = "Command output"
  mock_run.return_value = mock_result
  
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    
    # Create fleet file with service
    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text(TEST_FLEET_JSON)
    
    # Create service directory and executable
    service_dir = root_dir / "services" / TEST_SERVICE_LABEL
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    request = RunRequest(
      executable_path=str(script_file),
      root_directory=str(root_dir),
      create_root=True,
      debug=True
    )
    
    response = handle(request)
    assert not response.errors
    assert "Command executed successfully" in response.output
    assert "Command output" in response.output
    assert f"Found {TEST_SERVICE_LABEL} service" in response.output
    mock_ensure_dir.assert_called_once()


def test_handle_gracefully_handles_unexpected_exceptions():
  """Test that handle gracefully catches and reports unexpected exceptions as errors."""
  # Create a request that will cause an exception in the try block
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)
    
    # Create invalid fleet file to trigger JSON decode error in Device.load_all
    fleet_file = root_dir / "fleet.json"
    fleet_file.write_text("invalid json{{}")
    
    # Create service and executable
    service_dir = root_dir / "services" / "test"
    service_dir.mkdir(parents=True)
    script_file = service_dir / "init"
    script_file.write_text("#!/bin/bash\necho test")
    os.chmod(script_file, 0o755)
    
    # Mock Device.load_all to raise an exception
    with patch('mhs.run.logic.Device.load_all', side_effect=Exception("Test exception")):
      request = RunRequest(
        executable_path=str(script_file),
        root_directory=str(root_dir),
        debug=False
      )
      
      response = handle(request)
      assert response.errors
      assert "Test exception" in response.errors[0]

TEST_SERVICE_LABEL = "testing"
TEST_FLEET_JSON = """
{
	"devices": {
		"r-pi": {
			"description": "Raspberry Pi 3",
			"ssh_host": "ingress",
			"macs": ["B8:27:EB:AB:C0:DC"],
			"services": {
				"<<service-label>>": {
					"port": 59999
				}
			}
		}
	}
}
""".strip().replace("<<service-label>>", TEST_SERVICE_LABEL)


@pytest.mark.integration
def test_end_to_end_service_execution_on_remote_host():
  """Integration test for complete service execution workflow on real remote host."""
  with tempfile.TemporaryDirectory() as temp_dir:
    root_dir = Path(temp_dir)

    test_fleet_file = root_dir / "fleet.json"
    test_fleet_file.write_text(TEST_FLEET_JSON)

    test_service_dir = root_dir / "services" / TEST_SERVICE_LABEL
    test_service_dir.mkdir(parents=True)
    test_lib_dir = root_dir / "lib"
    test_lib_dir.mkdir()

    test_global_env_file = root_dir / ".env"
    test_global_env_file.write_text("GLOBAL_VAR=1111")
    test_lib_file = test_lib_dir / "test.sh"
    test_lib_file.write_text("LIB_VAR=2222")
    test_service_env_file = test_service_dir / ".env"
    test_service_env_file.write_text("SERVICE_VAR=3333")
    test_service_command_file = test_service_dir / "init"
    test_service_command_file.write_text(
      "\n".join(
        [
          "#!/usr/bin/env bash",
          'echo "User: $(whoami)"',
          'echo "IP: $(hostname -I)"',
          'echo "Root: $(pwd)"',
          'source ".env"',
          'source "lib/test.sh"',
          f'source "services/{TEST_SERVICE_LABEL}/.env"',
          'echo "Global: $GLOBAL_VAR"',
          'echo "Lib: $LIB_VAR"',
          'echo "Service: $SERVICE_VAR"',
        ]
      ),
      newline="\n",
    )
    os.chmod(test_service_command_file, 0o755)

    try:
      request = RunRequest(
        executable_path=str(test_service_command_file),
        root_directory=str(root_dir),
        create_root=True,
        debug=False,
      )
      response = handle(request)
      assert not response.errors, f"Expected no errors but got: {response.errors}"
      assert "Command executed successfully" in response.output
    except Exception as e:
      assert False, f"Expected command to complete successfully but got: {e}"
