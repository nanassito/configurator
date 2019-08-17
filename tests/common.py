from dataclasses import dataclass
from typing import Any

from configurator.schemas import DictSchema


class TestException(Exception):
    pass


@dataclass(unsafe_hash=True)
class TestSimpleSchema(DictSchema):
    a: Any
    b: Any


@dataclass
class TestNestedSchema(DictSchema):
    simple: Any
    nested: TestSimpleSchema
