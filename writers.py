from dataclasses import fields, is_dataclass
from typing import Any, Callable, Dict
import json
import os
import logging

from configurator import Schema


LOGGER = logging.getLogger(__file__)


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


def json_formatter(config: Schema, sort_keys=True, indent=4, **kwargs) -> str:
    return json.dumps(
        dict_formatter(config), sort_keys=sort_keys, indent=indent, **kwargs
    )


def properties_formatter(config: Schema) -> str:
    data = {}
    for field in fields(config):
        field_value = getattr(config, field.name)
        if isinstance(field_value, bool):
            value = str(field_value).lower()
        else:
            value = str(field_value)
        data[field.name] = value
    return "\n".join([f"{key}={value}" for key, value in sorted(data.items())])


def file_writer(config: Schema, formatter: Callable[..., str], path: str) -> None:
    """Write configuration out to a file

    You probably want to use this in conjuction with `partial()` to define the
    path of where to write the configuration. For instance:

    In [1]: from functools import partial
    In [2]: writer = partial(
       ...:     file_writer,
       ...:     formatter=json_formatter,
       ...:     path="/tmp/test.json",
       ...: )
    In [3]: config = Config(Schema, writer, templates)
    In [4]: ConfigSet(configs=[config]).materialize()
    """
    data = formatter(config)
    directory = os.path.dirname(path)
    LOGGER.info(f"Making sure the directory '{directory}' exists.")
    os.makedirs(directory, exist_ok=True)
    with open(path, "w") as fd:
        LOGGER.info(f"Writting out configuration in '{path}'.")
        fd.write(data)
