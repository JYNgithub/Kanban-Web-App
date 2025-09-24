from pydantic import BaseModel

class Records(BaseModel):
    user_id: int
    name: str
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
