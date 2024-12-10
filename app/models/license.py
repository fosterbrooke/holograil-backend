from pydantic import BaseModel, Field
from typing import Optional

class License(BaseModel):
    user_id: str
    license_key: str
    expire_date: str
    device_number: Optional[str] = None  # Initially set to None