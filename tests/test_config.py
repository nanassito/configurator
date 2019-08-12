import pytest
from mock import Mock, call

from configurator import Config, Template
from tests.common import TestException, TestNestedSchema, TestSimpleSchema


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
        writer=Mock(),
        templates=templates,
        config_modifiers=modifiers,
        config_validators=[],
    )

    config.resolve()

    assert config.output == expected
    for modifier in modifiers:
        assert modifier.call_args == call(config.output)


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

    assert writer.call_args == call(TestSimpleSchema(a=1, b=2))


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


@pytest.mark.parametrize(
    ["validators"],
    [
        ([],),  # No validators
        ([Mock()],),  # Single validator
        ([Mock(), Mock(), Mock()],),  # Multiple validators
    ],
)
def test_validate_success(validators):
    config = Config(
        schema=TestSimpleSchema,
        writer=Mock(),
        templates=[Template(a=1, b=2)],
        config_modifiers=[],
        config_validators=validators,
    )
    config.resolve()

    config.validate()

    for validator in validators:
        assert validator.call_args == call(TestSimpleSchema(a=1, b=2))


@pytest.mark.parametrize(
    ["validators"],
    [
        ([Mock(side_effect=TestException)],),  # Unique fails
        ([Mock(side_effect=TestException), Mock(), Mock()],),  # First fails
        ([Mock(), Mock(side_effect=TestException), Mock()],),  # Any fails
        (
            # All fails
            [
                Mock(side_effect=TestException),
                Mock(side_effect=TestException),
                Mock(side_effect=TestException),
            ],
        ),
    ],
)
def test_validate_failure(validators):
    config = Config(
        schema=TestSimpleSchema,
        writer=Mock(),
        templates=[Template(a=1, b=2)],
        config_modifiers=[],
        config_validators=validators,
    )
    config.resolve()

    with pytest.raises(TestException):
        config.validate()
