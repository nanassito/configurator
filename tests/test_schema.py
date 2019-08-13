import pytest

from configurator.compiler import Template, instanciate_schema_from_template
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
