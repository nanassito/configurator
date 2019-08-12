import pytest
from mock import Mock, call

from configurator import ConfigSet
from tests.common import TestException, TestSimpleSchema


def create_and_attach_mock(mock_manager, name):
    mock = Mock()
    mock_manager.attach_mock(mock, name)
    return mock


def test_order_of_materialization():
    """Make sure that the materialize process happens in order.

    1. Resolve the configs
    4. Validate the configs
    5. Validate the configset
    6. Write the configs
    """
    mock_manager = Mock()
    config = Mock(output=TestSimpleSchema(a=1, b=2))
    mock_manager.attach_mock(config, "config")
    configset_modifier = create_and_attach_mock(mock_manager, "configset_modifier")
    configset_validator = create_and_attach_mock(mock_manager, "configset_validator")
    configset = ConfigSet(
        configs=[config],
        configset_modifiers=[configset_modifier],
        configset_validators=[configset_validator],
    )

    configset.materialize()

    assert mock_manager.mock_calls == [
        call.config.resolve(),
        call.configset_modifier([config.output]),
        call.config.validate(),
        call.configset_validator([config.output]),
        call.config.write(),
    ]


@pytest.mark.parametrize(
    ["config_validator", "configset_validator"],
    [
        (Mock(side_effect=TestException), Mock()),  # Config fails
        (Mock(), Mock(side_effect=TestException)),  # Configset fails
        # Both fails
        (Mock(side_effect=TestException), Mock(side_effect=TestException)),
    ],
)
def test_materialization_failures(config_validator, configset_validator):
    writer = Mock()
    config = Mock(writer=writer, validate=Mock(side_effect=config_validator))
    configset = ConfigSet(configs=[config], configset_validators=[configset_validator])

    with pytest.raises(TestException):
        configset.materialize()

    assert not writer.called
