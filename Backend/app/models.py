from pydantic import BaseModel
from typing import Optional

class ReportIn(BaseModel):
    name: str
    contact_details: Optional[str]
    issue_category: Optional[str]
    discription: Optional[str]
    manual_location_input: Optional[str]
    location_latitude: Optional[float]
    location_longitude: Optional[float]

class ReportOut(BaseModel):
    report_id: str
