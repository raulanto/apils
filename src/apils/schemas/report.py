from pydantic import BaseModel, ConfigDict
from typing import Any

class ReportSchemaConfig(BaseModel):
    totalColumns: int
    allColumns: list[str]
    visibleColumns: list[str]
    hiddenColumns: list[str]
    orderedColumns: list[str] | None = None
    pageSize: str | None = None

class ReportSortConfig(BaseModel):
    column: str
    direction: str  # "asc" or "desc"

class ReportHeatmapConfig(BaseModel):
    column: str
    direction: str  # "asc" or "desc"
    dataType: str

class ReportFilterConfig(BaseModel):
    column: str
    type: str
    values: list[Any] | None = None
    min: Any | None = None
    max: Any | None = None

class ReportRequestPayload(BaseModel):
    schema_: ReportSchemaConfig | None = None
    sort: ReportSortConfig | None = None
    heatmaps: list[ReportHeatmapConfig] | None = None
    filters: list[ReportFilterConfig] | None = None
    timestamp: str | None = None
    
    model_config = ConfigDict(populate_by_name=True)
    
    def __init__(self, **data):
        if "schema" in data:
            data["schema_"] = data.pop("schema")
        super().__init__(**data)
