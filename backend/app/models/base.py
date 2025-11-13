"""Base models module placeholder."""

from sqlmodel import SQLModel


class BaseModel(SQLModel):
    """Base class for all SQLModel entities."""

    class Config:
        arbitrary_types_allowed = True
