from dataclasses import dataclass
from textwrap import dedent
from typing import Any

import pytest

from configurator.compiler import Template, instanciate_schema_from_template
from configurator.schemas import DictSchema, JsonSchema, PropertiesSchema
from tests.common import TestNestedSchema, TestSimpleSchema


@pytest.mark.parametrize(
    ["schema", "template", "expected"],
    [
        (
            # Simple template
            TestSimpleSchema,
            Template(a=1, b=2),
            TestSimpleSchema(a=1, b=2),
        ),
        (
            # Nested template
            TestNestedSchema,
            Template(simple=1, nested=Template(a=1, b=2)),
            TestNestedSchema(simple=1, nested=TestSimpleSchema(a=1, b=2)),
        ),
    ],
)
def test_valid_instanciation(schema, template, expected):
    result = instanciate_schema_from_template(schema, template)

    assert result == expected


@pytest.mark.parametrize(
    ["schema", "template", "error"],
    [
        (TestSimpleSchema, Template(a=1), TypeError),
        (TestSimpleSchema, Template(a=1, b=2, c=3), TypeError),
    ],
)
def test_invalid_instanciation(schema, template, error):
    with pytest.raises(error):
        instanciate_schema_from_template(schema, template)


@dataclass(unsafe_hash=True)
class TestPropertiesSchema(PropertiesSchema):
    a: Any
    b: Any


@dataclass
class TestJsonSchema(JsonSchema):
    a: Any
    b: Any


test_cases = [
    {
        # Simple DictSchema
        "config": TestSimpleSchema(a=1, b="B"),
        "expected": {"a": 1, "b": "B"},
    },
    {
        # DictSchema nested in a DictSchema
        "config": TestNestedSchema(simple=1, nested=TestSimpleSchema(a=2.0, b="B")),
        "expected": {"simple": 1, "nested": {"a": 2.0, "b": "B"}},
    },
    {
        # Other schema nested in a DictSchema
        "config": TestNestedSchema(simple=1, nested=TestPropertiesSchema(a=2.0, b="B")),
        "expected": {"simple": 1, "nested": "a=2.0\nb=B"},
    },
    {
        # DictSchema with a list of types
        "config": TestSimpleSchema(a=1, b=[2, 3]),
        "expected": {"a": 1, "b": [2, 3]},
    },
    {
        # DictSchema with a list of DictSchema
        "config": TestSimpleSchema(a=1, b=[TestSimpleSchema(a=2.0, b="B"), 3]),
        "expected": {"a": 1, "b": [{"a": 2.0, "b": "B"}, 3]},
    },
    {
        # DictSchema with a set of simple types
        "config": TestSimpleSchema(a=1, b={2, 3}),
        "expected": {"a": 1, "b": {2, 3}},
    },
    {
        # DictSchema with a set of non-hashable schemas, note the fallback to list.
        "config": TestSimpleSchema(a=1, b={TestSimpleSchema(a=2.0, b="B")}),
        "expected": {"a": 1, "b": [{"a": 2.0, "b": "B"}]},
    },
    {
        # DictSchema with a set of hashable schemas, note the fallback to list.
        "config": TestSimpleSchema(a=1, b={TestPropertiesSchema(a=2.0, b="B")}),
        "expected": {"a": 1, "b": {"a=2.0\nb=B"}},
    },
    {
        # DictSchema with a map of simple types
        "config": TestSimpleSchema(a=1, b={"c": 3}),
        "expected": {"a": 1, "b": {"c": 3}},
    },
    {
        # DictSchema with a map of schemas
        "config": TestSimpleSchema(a=1, b={"c": TestSimpleSchema(a=2.0, b="B")}),
        "expected": {"a": 1, "b": {"c": {"a": 2.0, "b": "B"}}},
    },
    {
        # Simple properties schema
        "config": TestPropertiesSchema(a=1, b="B"),
        "expected": dedent(
            """
                a=1
                b=B
            """
        ).strip(),
    },
    {
        # Properties schema handling floats and booleans
        "config": TestPropertiesSchema(a=1.0, b=False),
        "expected": dedent(
            """
                a=1.0
                b=false
            """
        ).strip(),
    },
    {
        # Properties schema handling nesting another schema
        "config": TestPropertiesSchema(
            a=TestPropertiesSchema(a=1, b="B"), b=TestSimpleSchema(a=2, b="C")
        ),
        "expected": dedent(
            """
                a=a=1\\
                b=B
                b={'a': 2, 'b': 'C'}
            """
        ).strip(),
    },
    {
        # Properties schema handling backslash and unicode
        "config": TestPropertiesSchema(a="values\\with\\backslash", b="unicode™"),
        "expected": dedent(
            """
                a=values\\\\with\\\\backslash
                b=unicode\\u2122
            """
        ).strip(),
    },
    {
        # Properties schema handling multiline values.
        "config": TestPropertiesSchema(
            "multiple\nlines",
            b=dedent(
                """
                    more
                    lines
                """
            ).strip(),
        ),
        "expected": dedent(
            """
                a=multiple\\
                lines
                b=more\\
                lines
            """
        ).strip(),
    },
    {
        # Simple Json
        "config": TestJsonSchema(a=1, b="B"),
        "expected": dedent(
            """
                {
                    "a": 1,
                    "b": "B"
                }
            """
        ).strip(),
    },
    {
        # Serialized Json in a Json value
        "config": TestJsonSchema(a=1.0, b=TestJsonSchema(a=None, b=True)),
        "expected": dedent(
            """
                {
                    "a": 1.0,
                    "b": "{\\n    \\"a\\": null,\\n    \\"b\\": true\\n}"
                }
            """
        ).strip(),
    },
    {
        # Dict in a Json
        "config": TestJsonSchema(a=1.0, b=TestSimpleSchema(a=None, b=True)),
        "expected": dedent(
            """
                {
                    "a": 1.0,
                    "b": {
                        "a": null,
                        "b": true
                    }
                }
            """
        ).strip(),
    },
]


@pytest.mark.parametrize(
    ["config", "expected"], [(test["config"], test["expected"]) for test in test_cases]
)
def test_serialization(config, expected):
    assert config.serialize() == expected
