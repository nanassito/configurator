import pytest

from configurator import Template


@pytest.mark.parametrize(
    ["source", "other", "expected", "msg"],
    [
        ({"a": 1}, {"a": 2}, {"a": 2}, "Simple template with one field."),
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}, "Adding a new field."),
        ({"a": 1}, {"a": lambda x: x + 10}, {"a": 11}, "Applying a function."),
        (
            {"a": Template(b=1)},
            {"a": Template(c=2)},
            {"a": Template(b=1, c=2)},
            "Merging a sub template.",
        ),
        (
            {"a": 1},
            {"a": Template(c=2)},
            {"a": Template(c=2)},
            "Merging a sub template onto a primitive type.",
        ),
        (
            {"a": Template(c=2)},
            {"a": 1},
            {"a": 1},
            "Merging a primitive type onto a sub template.",
        ),
    ],
)
def test_template_merge(source, other, expected, msg):
    result = Template(**source)
    result.merge_from(Template(**other))

    assert result == Template(**expected), msg
