import json
import string
from collections import Hashable
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Dict


@dataclass
class Schema(object):
    """Define the fields the final configuration is expected to have.

    You should not be instanciating this yourself.
    """

    def serialize(self: "Schema") -> Any:
        """Serialize the configuration to a format expected by the writer.

        The format will change from writer to writer so we can't provide a good
        default implementation nor typing. However we do provide subclasses with
        their own serialization for the common use cases.
        """
        raise NotImplementedError("You need to implement the `serialize()`.")


@dataclass
class DictSchema(Schema):
    """Schema of a configuration that will be serialized as a dictionary."""

    def serialize(self: "DictSchema") -> Dict[str, Any]:
        data = {}
        for field in fields(self):
            field_value = getattr(self, field.name)
            if isinstance(field_value, list):
                value = [
                    element.serialize() if is_dataclass(element) else element
                    for element in field_value
                ]
            elif isinstance(field_value, set):
                # Note, sets are persisted as list if at least one element is a
                # complex type because we won't be able to hash the resulting map.
                hashable = True
                value = []
                for element in field_value:
                    if isinstance(element, Schema):
                        element = element.serialize()
                    hashable &= isinstance(element, Hashable)
                    value.append(element)
                if hashable:
                    value = set(value)
            elif isinstance(field_value, dict):
                value = {
                    key: element.serialize() if isinstance(element, Schema) else element
                    for key, element in field_value.items()
                }
            elif isinstance(field_value, Schema):
                value = field_value.serialize()
            else:
                value = field_value
            data[field.name] = value
        return data


@dataclass
class JsonSchema(DictSchema):
    """Schema of a configuration that will be serialized as a json.

    Note that nested object will need to be DictSchema if you want them to also
    be represented as json.
    """

    def serialize(self: "JsonSchema") -> str:
        return json.dumps(super().serialize(), sort_keys=True, indent=4)


@dataclass
class PropertiesSchema(Schema):
    """Schema of a configuration that will be serialized as a properties file."""

    @staticmethod
    def encode(value: str) -> str:
        translation_table = {
            # Handle unicode characters
            ord(char): "\\u" + hex(ord(char))[2:]
            for char in value
            if char not in string.printable
        }
        translation_table.update({ord("\n"): "\\\n", ord("\\"): "\\\\"})
        return value.translate(translation_table)

    def serialize(self: "PropertiesSchema") -> str:
        data = {}
        for field in fields(self):
            field_value = getattr(self, field.name)
            if isinstance(field_value, Schema):
                value = str(field_value.serialize())
            elif isinstance(field_value, bool):
                value = str(field_value).lower()
            else:
                value = str(field_value)
            data[field.name] = PropertiesSchema.encode(value)
        return "\n".join([f"{key}={value}" for key, value in sorted(data.items())])
