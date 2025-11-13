"""Base schema module placeholder."""

from pydantic import BaseModel as PydanticBaseModel


class SchemaBase(PydanticBaseModel):
    """Base schema for shared attributes."""

    class Config:
        orm_mode = True
