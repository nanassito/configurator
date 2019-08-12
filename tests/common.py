from dataclasses import dataclass
from typing import Any

from configurator import Schema


@dataclass
class TestSimpleSchema(Schema):
    a: Any
    b: Any


@dataclass
class TestNestedSchema(Schema):
    simple: Any
    nested: TestSimpleSchema
