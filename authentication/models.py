from pydantic import BaseModel,Field
from uuid import UUID, uuid4

class NewUser(BaseModel):
    username : str|None =None
    email : str
    mobile : str
    otp : str

class UserLogin(BaseModel):
    email:str|None =None
    otp : str