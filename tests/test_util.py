from pathlib import Path

import pytest

from mhs.util import to_camel_case, to_dotpath, to_snake_case


@pytest.mark.parametrize(
  "input_text,expected",
  [
    ("MyAction", "myaction"),
    ("My Action", "my_action"),
    ("my-action", "my_action"),
    ("my.action", "my_action"),
    ("MyAction123", "myaction123"),
    ("My__Action", "my_action"),
    ("  My Action  ", "my_action"),
  ],
)
def test_to_snake_case(input_text, expected):
  assert to_snake_case(input_text) == expected


@pytest.mark.parametrize(
  "input_text,expected",
  [
    ("my_action", "MyAction"),
    ("my action", "MyAction"),
    ("my-action", "MyAction"),
    ("my.action", "MyAction"),
    ("myAction", "Myaction"),
    ("My Action 123", "MyAction123"),
  ],
)
def test_to_camel_case(input_text, expected):
  assert to_camel_case(input_text) == expected


@pytest.mark.parametrize(
  "input_path,expected",
  [
    (Path("foo.bar.baz"), "foo.bar.baz"),
    (Path("foo/bar/baz"), "foo.bar.baz"),
    (Path("foo\\bar\\baz"), "foo.bar.baz"),
    (Path("foo/bar-baz"), "foo.bar-baz"),
  ],
)
def test_to_dotpath(input_path, expected):
  assert to_dotpath(input_path) == expected
