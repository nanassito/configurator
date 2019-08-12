from dataclasses import dataclass, fields
from typing import Callable, List, Type


@dataclass
class Schema(object):
    """Define the fields the final configuration is expected to have.

    You should not be instanciating this yourself.
    """

    pass


class Template(object):
    """Configuration template.

    You can instanciate this with any field you wish. Templates have the ability
    to merge data from  another template.
    """

    def __init__(self: "Template", **kwargs) -> None:
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self: "Template", other: object) -> bool:
        if self.fields != getattr(other, "fields", []):
            return False
        for field in self.fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    def merge_from(self: "Template", other: "Template") -> None:
        for field in other.fields:
            field_value = getattr(other, field)
            if field not in self.fields:
                self.fields.append(field)
                setattr(self, field, field_value)
            if callable(field_value):
                setattr(self, field, field_value(getattr(self, field)))
            elif isinstance(field_value, Template) and isinstance(
                getattr(self, field), Template
            ):
                getattr(self, field).merge_from(field_value)
            else:
                setattr(self, field, field_value)


UNSET = "__CONFIGURATOR_UNSET_FIELD"


def instanciate_schema_from_template(
    schema: Type[Schema], template: Template
) -> Schema:
    """Instanciate a Schema from a list of Templates."""
    spec = {}
    expected_fields = {f.name for f in fields(schema)}
    differences = expected_fields.symmetric_difference(template.fields)
    if differences:
        raise TypeError(
            f"Attributes mismatch between the Schema and Template: {differences}"
        )
    for field in fields(schema):
        if field.name in template.fields:
            template_value = getattr(template, field.name)
            if isinstance(template_value, Template):
                value = instanciate_schema_from_template(field.type, template_value)
            else:
                value = template_value
            spec[field.name] = value
        if spec[field.name] == UNSET:
            del spec[field.name]
    return schema(**spec)  # type: ignore


class Config(object):
    __slots__ = [
        "config_modifiers",
        "config_validators",
        "output",
        "schema",
        "templates",
        "writer",
    ]

    def __init__(
        self: "Config",
        schema: Type[Schema],
        writer: Callable[[Schema], None],
        templates: List[Template] = None,
        config_modifiers: List[Callable[[Schema], None]] = None,
        config_validators: List[Callable[[Schema], None]] = None,
    ):
        self.schema: Type[Schema] = schema
        self.writer = writer
        self.templates = templates or []
        self.config_modifiers = config_modifiers or []
        self.config_validators = config_validators or []

    def resolve(self: "Config") -> None:
        """Resolve the configuration.

        We first create a new object from the templates in order, then apply the
        modifiers in order.
        """
        # Create a flat template by merging all the templates
        flat_template = Template()
        for template in self.templates:
            flat_template.merge_from(template)
        # Create new object from the flat template
        self.output = instanciate_schema_from_template(self.schema, flat_template)
        # Apply modifiers
        for modifier in self.config_modifiers:
            modifier(self.output)

    def write(self: "Config") -> None:
        """Write the config file out using the provided writer."""
        self.writer(self.output)


if __name__ == "__main__":
    raise Exception("Configurator is not meant to be run directly.")
