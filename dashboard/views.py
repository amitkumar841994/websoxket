from fastapi import APIRouter,Depends,Request,HTTPException
import uuid
from config import db,manager,tigger_mongo
import json
from fastapi.responses import RedirectResponse
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi import WebSocket, WebSocketDisconnect
from dashboard.models import SaveContact


load_dotenv()

class Contact:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/save_contact/", self.save_contact, methods=["POST"])

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

            # Save to MongoDB
                await self.messages_collection.insert_one({
                    "user_id": user_id,
                    "message": data,
                    "timestamp": datetime.utcnow()
                })

            await manager.broadcast(f"{user_id}: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            await manager.broadcast(f"{user_id} left the chat.")
            print(f"{user_id} left the chat.")
        