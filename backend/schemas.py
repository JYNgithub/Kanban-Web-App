from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    status: str

    model_config = {
        "from_attributes": True
    }
