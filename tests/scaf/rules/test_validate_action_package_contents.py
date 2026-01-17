import pytest

from scaf.rules.pure import validate_action_package_contents


def test_valid_package_with_command():
  filenames = {"__init__.py", "handler.py", "command.py"}
  # Should not raise
  validate_action_package_contents(filenames)


def test_valid_package_with_query():
  filenames = {"__init__.py", "handler.py", "query.py"}
  # Should not raise
  validate_action_package_contents(filenames)


def test_missing_init():
  filenames = {"handler.py", "command.py"}
  with pytest.raises(RuntimeError) as exc:
    validate_action_package_contents(filenames)
  assert "__init__.py" in str(exc.value)


def test_missing_handler():
  filenames = {"__init__.py", "command.py"}
  with pytest.raises(RuntimeError) as exc:
    validate_action_package_contents(filenames)
  assert "handler.py" in str(exc.value)


def test_missing_both_init_and_handler():
  filenames = {"command.py"}
  with pytest.raises(RuntimeError) as exc:
    validate_action_package_contents(filenames)
  msg = str(exc.value)
  assert "__init__.py" in msg
  assert "handler.py" in msg


def test_missing_both_command_and_query():
  filenames = {"__init__.py", "handler.py"}
  with pytest.raises(RuntimeError) as exc:
    validate_action_package_contents(filenames)
  assert "command.py or query.py" in str(exc.value)


def test_multiple_failures_combined():
  filenames = {"junk.py"}
  with pytest.raises(RuntimeError) as exc:
    validate_action_package_contents(filenames)
  msg = str(exc.value)
  assert "__init__.py" in msg
  assert "handler.py" in msg
  assert "command.py or query.py" in msg
