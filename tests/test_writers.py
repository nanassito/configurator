import pytest
from writers import dict_formatter

from tests.common import TestNestedSchema, TestSimpleSchema


@pytest.mark.parametrize(
    ["config", "expected"],
    [
        (TestSimpleSchema(a=1, b="B"), {"a": 1, "b": "B"}),  # Simple Schema
        (
            # Nested Schema
            TestNestedSchema(simple=1, nested=TestSimpleSchema(a=2.0, b="B")),
            {"simple": 1, "nested": {"a": 2.0, "b": "B"}},
        ),
        # List of simple types
        (TestSimpleSchema(a=1, b=[2, 3]), {"a": 1, "b": [2, 3]}),
        # List of Schemas
        (
            TestSimpleSchema(a=1, b=[TestSimpleSchema(a=2.0, b="B"), 3]),
            {"a": 1, "b": [{"a": 2.0, "b": "B"}, 3]},
        ),
        # Set of simple types
        (TestSimpleSchema(a=1, b={2, 3}), {"a": 1, "b": {2, 3}}),
        # Set of Schemas, note the fallback to list.
        (
            TestSimpleSchema(a=1, b={TestSimpleSchema(a=2.0, b="B")}),
            {"a": 1, "b": [{"a": 2.0, "b": "B"}]},
        ),
        # Dict of simple types
        (TestSimpleSchema(a=1, b={"c": 3}), {"a": 1, "b": {"c": 3}}),
        # Dict of Schemas, note the fallback to list.
        (
            TestSimpleSchema(a=1, b={"c": TestSimpleSchema(a=2.0, b="B")}),
            {"a": 1, "b": {"c": {"a": 2.0, "b": "B"}}},
        ),
    ],
)
def test_dict_formatter(config, expected):
    assert dict_formatter(config) == expected
