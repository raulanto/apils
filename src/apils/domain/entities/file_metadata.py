from dataclasses import dataclass
from typing import Any

@dataclass
class ColumnMetadata:
    name: str
    dtype: str
    is_text: bool
    is_numeric: bool
    is_date: bool
    unique_values: list[Any] | None = None  # For text/catalog
    min_value: Any | None = None            # For numeric/date
    max_value: Any | None = None            # For numeric/date

@dataclass
class FileMetadata:
    filename: str
    total_rows: int
    columns: list[ColumnMetadata]
