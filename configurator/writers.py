from dataclasses import fields, is_dataclass
from typing import Any, Callable, Dict
import json
import os
import logging

from configurator.compiler import Schema


LOGGER = logging.getLogger(__file__)


def file_writer(config: Schema, path: str) -> None:
    """Write configuration out to a file

    You probably want to use this in conjuction with `partial()` to define the
    path of where to write the configuration. For instance:

    In [1]: from functools import partial
    In [2]: writer = partial(file_writer, path="/tmp/test.json")
    In [3]: config = Config(Schema, writer, templates)
    In [4]: ConfigSet(configs=[config]).materialize()
    """
    LOGGER.debug(f"Serializing configuration: {config}")
    data = config.serialize()
    directory = os.path.dirname(path)
    LOGGER.info(f"Making sure the directory '{directory}' exists.")
    os.makedirs(directory, exist_ok=True)
    with open(path, "w") as fd:
        LOGGER.info(f"Writting out configuration in '{path}'.")
        fd.write(data + "\n")
