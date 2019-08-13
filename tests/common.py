from dataclasses import dataclass
from typing import Any

from configurator.compiler import Schema


class TestException(Exception):
    pass


@dataclass(unsafe_hash=True)
class TestSimpleSchema(Schema):
    a: Any
    b: Any


@dataclass
class TestNestedSchema(Schema):
    simple: Any
    nested: TestSimpleSchema
