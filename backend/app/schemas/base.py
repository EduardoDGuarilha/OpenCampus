"""Base schema module placeholder."""

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class SchemaBase(PydanticBaseModel):
    """Base schema for shared attributes."""

    model_config = ConfigDict(from_attributes=True)
