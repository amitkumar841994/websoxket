from fastapi import APIRouter,Depends,Request,HTTPException
from authentication.models import NewUser,UserLogin
import uuid
from config import db
# from utils.access_token_handler import pwd_context,create_access_token,create_refresh_token
import json
from fastapi.responses import RedirectResponse
import uuid
import secrets
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from aiosmtplib import send
from email.message import EmailMessage
load_dotenv()

class NewUserRegistration:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/register", self.register, methods=["POST"])
        self.router.add_api_route("/otp", self.create_otp, methods=["POST"])


    async def register(self, new_user:NewUser):

        try:
            result = await db.User.find_one({ '$or': [{'email':new_user.email}, {'mobile':new_user.mobile}]})
            otp = await db.OTP.find_one({"email": new_user.email},sort=[("_id", -1)])

            if result:
                if otp["otp"] == new_user.otp:
                    return {
                        "message": "Logedin successfully",
                        "status_code":200
                        }
                else:
                    return {
                        "message": "OTP is not valid",
                        "status_code":400
                        }
    
            else :   

                if otp["otp"] == new_user.otp:
                    print(">>>>>>>>>>",type(new_user))
                
                    result = db.User.insert_one(new_user.model_dump(exclude="otp"))
                    return {
                        "message": "Logedin successfully",
                        "status_code":200
                        }
                else:
                    return {
                        "message": "OTP is not valid",
                        "status_code":400
                        }
        except Exception as e:
            return {
                    "message": f"{str(e)}",
                    "status_code":500
                    }
    


    async def create_otp(self,request: Request):
        try:
            body = await request.json()
            email=body["email"]
            otp = random.randint(100000, 999999)  # Generate 6-digit OTP
            expiry = datetime.utcnow() + timedelta(minutes=5)

            otp_data = {
                "email": email,  # e.g., email or phone
                "otp": str(otp),
                "expires_at": expiry,
                "created_at": datetime.utcnow()
            }

            await db.OTP.insert_one(otp_data)
            await self.send_email(email,otp)

            return {"status":200,"success":True, "message": "OTP created successfully"}
        except Exception as e:
            print("otp is not working",e)
            return {"status":400,"success":False,"message": str(e)}


    async def send_email(self,to_email: str,otp: str):

        subject = "Your One-Time Password (OTP)"
        content = f"Your OTP is {otp}. It will expire in 5 minutes. Do not share this with anyone."
        message = EmailMessage()
        message["From"] = "amitkumat841994@gmail.com"       # Replace with your email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(content)

        try:
            await send(
                message,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username="amitkumar841994@gmail.com",       # Gmail or SMTP username
                password="crtq lfqi avrr ngus")          
            return {"status": "success", "message": f"Email sent to {to_email}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}