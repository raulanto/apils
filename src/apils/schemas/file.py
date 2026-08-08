from pydantic import BaseModel, ConfigDict
from typing import Any


class ColumnSchema(BaseModel):
    name: str
    dtype: str
    is_text: bool
    is_numeric: bool
    is_date: bool
    unique_values: list[Any] | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    
    model_config = ConfigDict(from_attributes=True)


class FileResponseSchema(BaseModel):
    id: str
    filename: str
    total_rows: int
    columns: list[ColumnSchema]

    model_config = ConfigDict(from_attributes=True)
