from pydantic import BaseModel

class Records(BaseModel):
    user_id: int
    name: str
    email: str
    phone_number: str
    organization: str
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
