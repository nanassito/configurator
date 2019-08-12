from mock import Mock
import pytest

from configurator import Config, Template
from tests.common import TestNestedSchema, TestSimpleSchema


@pytest.mark.parametrize(
    ["schema", "templates", "modifiers", "expected"],
    [
        (
            # Simple case with just one template
            TestSimpleSchema,
            [Template(a=1, b=2)],
            [],
            TestSimpleSchema(a=1, b=2),
        ),
        (
            # Multiple templates
            TestSimpleSchema,
            [Template(a=1), Template(b=2)],
            [],
            TestSimpleSchema(a=1, b=2),
        ),
        (
            # Modifiers
            TestSimpleSchema,
            [Template(a=1, b=2)],
            [Mock(), Mock()],
            TestSimpleSchema(a=1, b=2),
        ),
        (
            # Nested schemas
            TestNestedSchema,
            [Template(simple=3, nested=Template(a=1, b=2))],
            [Mock(), Mock()],
            TestNestedSchema(simple=3, nested=TestSimpleSchema(a=1, b=2)),
        ),
    ],
)
def test_resolve(schema, templates, modifiers, expected):
    config = Config(
        schema=schema,
        writer=lambda x: x,
        templates=templates,
        config_modifiers=modifiers,
        config_validators=[],
    )
    config.resolve()

    assert config.output == expected
    for modifier in modifiers:
        assert modifier.call_args == ((config.output,), {})


def test_writer_is_called():
    writer = Mock()
    config = Config(
        schema=TestSimpleSchema,
        writer=writer,
        templates=[Template(a=1, b=2)],
        config_modifiers=[],
        config_validators=[],
    )
    config.resolve()
    config.write()

    assert writer.call_args == ((TestSimpleSchema(a=1, b=2),), {})


def test_fail_if_writer_is_called_before_resolve():
    writer = Mock()
    config = Config(
        schema=TestSimpleSchema,
        writer=writer,
        templates=[Template(a=1, b=2)],
        config_modifiers=[],
        config_validators=[],
    )

    with pytest.raises(AttributeError):
        config.write()
    assert not writer.called