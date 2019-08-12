from dataclasses import fields, is_dataclass
from typing import Any, Dict
import json
import os

from configurator import Schema


def dict_formatter(config: Schema) -> Dict[str, Any]:
    data = {}
    for field in fields(config):
        field_value = getattr(config, field.name)
        if isinstance(field_value, list):
            value = [
                dict_formatter(element) if is_dataclass(element) else element
                for element in field_value
            ]
        elif isinstance(field_value, set):
            # Note, sets are persisted as list if at least one element is a
            # complex type because we won't be ablet to hash the resulting map.
            hashable = True
            value = []
            for element in field_value:
                if is_dataclass(element):
                    hashable = False
                    value.append(dict_formatter(element))
                else:
                    value.append(element)
            if hashable:
                value = set(value)
        elif isinstance(field_value, dict):
            value = {
                key: dict_formatter(element) if is_dataclass(element) else element
                for key, element in field_value.items()
            }
        elif isinstance(field_value, Schema):
            value = dict_formatter(field_value)
        else:
            value = field_value
        data[field.name] = value
    return data


def json_writer(config: Schema, path: str) -> None:
    """Write configuration in json format.

    You probably want to use this in conjuction with `partial()` to define the
    path of where to write the configuration. For instance:

    In [1]: from functools import partial
    In [2]: writer = partial(json_writer, path="/tmp/test.json")
    In [3]: config = Config(Schema, writer, templates)
    In [4]: ConfigSet(configs=[config]).materialize()
    """
    data = dict_formatter(config)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fd:
        json.dump(data, fd)
