from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DocumentDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doc_code: str
    gateway_name: str | None
    doc_type: str
    version_code: str
    title: str
    effective_from: date
    effective_to: date | None
    source_path: str
    created_at: datetime
