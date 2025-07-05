from pydantic import BaseModel,Field
from uuid import UUID, uuid4

class SaveContact(BaseModel):
    name : str
    email : str
    mobile : str
    saved_by : str