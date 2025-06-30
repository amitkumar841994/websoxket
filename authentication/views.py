from fastapi import APIRouter,Depends,Request,HTTPException
from authentication.models import NewUser,UserLogin
import uuid
from config import db
from utils.access_token_handler import pwd_context,create_access_token,create_refresh_token
import json
from fastapi.responses import RedirectResponse
import uuid
import secrets

from dotenv import load_dotenv
import os
load_dotenv()

class NewUserRegistration:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.router.add_api_route("/login", self.user_login, methods=["POST"])
        self.router.add_api_route("/login1", self.login, methods=["GET"])
        self.router.add_api_route("/auth_login", self.auth, methods=["GET"],name="login2")


    async def register(self, new_user:NewUser):
        if not new_user.user_id:
            new_user.user_id = uuid.uuid4()

        try:
            result = db.User.find_one({ '$or': [{'email':new_user.email}, {'mobile':new_user.mobile}]})
            print("User>>>>>>>", result)
            if result:
                if new_user.email== result['email'] :
                    return {  "message": f"{new_user.email} already registered"}
                if new_user.mobile== result['mobile'] :
                    return {  "message": f"{new_user.mobile} already registered"}   
            else :   
                new_user.password =pwd_context.hash(new_user.password)  
                result = db.User.insert_one(new_user.model_dump())
                return {
                    "message": "registered successfully",
                    "data": new_user.model_dump(),
                    "status_code":201
                    }
        except Exception as e:
            return {
                    "message": f"{str(e)}",
                    "status_code":500
                    }