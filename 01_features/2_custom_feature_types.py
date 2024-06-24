import attrs
from dataclasses import dataclass
from pydantic import BaseModel, constr
from typing import Optional

from chalk.features import features, feature


# A dataclass can be used as a feature (Book.jacket_info below)
@dataclass
class JacketInfo:
    title: str
    subtitle: str
    body: str


# Pydantic classes can also be used as features (Book.title below)
class TitleInfo(BaseModel):
    heading: constr(min_length=2)
    subheading: Optional[str]


# attrs classes are also valid for feature types (Book.table_of_contents below)
@attrs.define
class TableOfContentsItem:
    foo: str
    bar: int


@features
class Book:
    id: int
    # You can use any `dataclass` as a struct feature.
    # Struct types should be used for objects that don't have ids.
    # If an object has an id, consider using has_one.
    jacket_info: JacketInfo

    # If you prefer `pydantic` to `dataclass`, you can use that instead.
    title: TitleInfo

    # Alternatively, you can use `attrs`. Any of these struct types
    # (`dataclass`, `pydantic`, and `attrs`) can be used with
    # `set[...]` or `list[...]`.
    table_of_contents: list[TableOfContentsItem]


# Finally, if you have an object that you want to serialize that isn't
# from `dataclass`, `attrs`, or `pydantic`, you can write a custom codec.

# Consider the custom class below:
class CustomStruct:
    def __init__(self, foo: str, bar: int) -> None:
        self.foo = foo
        self.bar = bar

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CustomStruct)
            and self.foo == other.bar
            and self.bar == other.bar
        )

    def __hash__(self) -> int:
        return hash((self.foo, self.bar))


@dataclass
class CustomStructDC(BaseModel):
    foo: str
    bar: int


@features
class Book:
    id: int
    jacket_info: JacketInfo
    title: TitleInfo
    table_of_contents: list[TableOfContentsItem]
    custom_field: CustomStructDC = feature(
        # The encoder takes an instance of the custom type and outputs a Python object
        encoder=lambda x: CustomStructDC(foo=x.foo, bar=x.bar),
        # The decoder takes output of the encoder and creates an instance of the custom type
        decoder=lambda x: CustomStruct(**x),
    )
