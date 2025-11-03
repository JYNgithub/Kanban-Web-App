from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class Records(BaseModel):
    user_id: Optional[int] = None
    name: str
    revenue: Decimal | None = None
    email: str | None = None
    phone_number: str | None = None
    organization: str | None = None
    description: str | None = None
    status: str

    model_config = {
        "from_attributes": True
    }

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
