from fastapi import APIRouter,Depends,Request,HTTPException
import uuid
from config import db,manager
import json
from fastapi.responses import RedirectResponse
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi import WebSocket, WebSocketDisconnect
from dashboard.models import SaveContact
from typing import Optional



load_dotenv()

class Contact:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/save_contact/", self.save_contact, methods=["POST"])
        self.router.add_api_route("/contact/",self.fetch_contact,methods=["GET"])

    async def save_contact(self,new_contact:SaveContact):
        try:
            contact_dict =new_contact.model_dump()
            contact_dict["_id"] = contact_dict.pop("email")

            resp = await db.Contact.find_one({"_id":contact_dict["_id"]})
            print("resp>>>>>>>>>",resp)
            if resp:
                return {
                "message": "user already exist",
                "UserDetails": False,
                "status_code":400
                }
            else:
                is_registered = await db.User.find_one({"_id":contact_dict["_id"]})
                if is_registered:
                    contact_dict["is_registered"] = True
                else:
                    contact_dict["is_registered"] = False


                db.Contact.insert_one(contact_dict)
            
                return {
                    "message": "Saved successfuly",
                    "UserDetails": True,
                    "status_code":200
                }
        except Exception as e:
            print("error is here>>>>",e)
            return {
                    "message": str(e),
                    "UserDetails": False,
                    "status_code":400
                }
    
    

    async def fetch_contact(self,request:Request):
        username = request.query_params.get("username") 
        try:
            if username is None:
                return {
                    "message": "Username is NuLL",
                    "status_code":400
                }
            results = []
            resp = db.Contact.find({"saved_by":username})
            async for doc in resp:
                results.append(doc)
            

            print("username is>>>>>>>>1111",username)
            return {
                            "data": results,
                            "status_code":200
                            }
        except Exception as e:
            return{"message":str(e),"status_code":500}
        

class SendMessage:
    def __init__(self):
        self.router =APIRouter()
  
        self.router.add_api_websocket_route('/message/sender/{user_id}',self.sender)
        self.messages_collection = db["Messages"]


    async def sender(self, websocket: WebSocket, user_id: str):  # changed 'username' -> 'user_id'
        print("WebSocket connection attempt by:", user_id)
        await manager.connect(websocket)  

        try:
            while True:
                data = await websocket.receive_text()
                data = json.loads(data)

                # Save to MongoDB
                await self.messages_collection.insert_one({
                    "sender": user_id,
                    "receiver": data.get("receiver"),
                    "message": data.get("message"),
                    "timestamp": datetime.now(),
                    "status": "sent",
                    # "chat_id": "amit841994@gmail.com__receiver@example.com"
                })

                await manager.broadcast(f"{user_id}: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"{user_id} left the chat.")
            print(f"{user_id} left the chat.")
        

    async def reciver(self,websocket:WebSocket,user_id: str):
        pass
        