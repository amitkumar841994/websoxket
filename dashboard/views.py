from fastapi import APIRouter,Depends,Request,HTTPException
import uuid
from config import db,manager
import json
from fastapi.responses import RedirectResponse,StreamingResponse
import uuid
from datetime import datetime, timedelta
from datetime import datetime

from dotenv import load_dotenv
import os
from fastapi import WebSocket, WebSocketDisconnect
from dashboard.models import SaveContact
from typing import Optional
import asyncio
import aiohttp
import time



load_dotenv()

class Contact:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route("/save_contact/", self.save_contact, methods=["POST"])
        self.router.add_api_route("/contact/",self.fetch_contact,methods=["GET"])

    async def save_contact(self,new_contact:SaveContact):
        try:
            contact_dict =new_contact.model_dump()
            # contact_dict["_id"] = contact_dict.pop("email")

            resp = await db.Contact.find_one({"email":contact_dict["email"]})
            print("resp>>>>>>>>>",resp,)
            if resp:
                if resp["saved_by"] == contact_dict["saved_by"]:
                    return {
                    "message": "user already exist",
                    "UserDetails": False,
                    "status_code":400
                    }
                else:
                    is_registered = await db.User.find_one({"_id":contact_dict["email"]})
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
            else:
                    is_registered = await db.User.find_one({"_id":contact_dict["email"]})
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
            resp =  db.Contact.find({"saved_by":username})
            async for doc in resp:
                doc["_id"] = str(doc["_id"])
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
        self.router.add_api_route('/message/reciver/',self.get_chat_history,methods=["GET"])
        # self.router.add_api_route('/send_offer',self.send_offer,methods=["POST"])
        self.router.add_api_websocket_route('/send_offer/{user_id}',self.send_offer)
        self.messages_collection = db["Messages"]


    async def sender(self, websocket: WebSocket, user_id: str):  # changed 'username' -> 'user_id'
        print("WebSocket connection attempt by:", user_id)
        await manager.connect(websocket,user_id)  

        try:
            while True:
                data = await websocket.receive_text()
                data = json.loads(data)
                print("DATA IS<<<<<<<<",data)
                

                # Save to MongoDB
                await self.messages_collection.insert_one({
                    "sender": user_id,
                    "receiver": data.get("receiver"),
                    "message": data.get("message"),
                    "timestamp": datetime.now(),
                    "status": "sent",
                    # "chat_id": "amit841994@gmail.com__receiver@example.com"
                })

                # await manager.broadcast(f"{user_id}: {data}")
                # await manager.send_personal_message(f"{user_id}: {data.get("message")}", data.get("receiver"))
                await manager.send_personal_message(json.dumps({
                    "sender": user_id,
                    "receiver": data.get("receiver"),
                    "message": data.get("message"),
                    "timestamp": datetime.now().isoformat()
                }), data.get("receiver"))
        except WebSocketDisconnect:
            manager.disconnect(websocket,user_id)
            # await manager.broadcst(f"{user_id} left the chat.")
            # print(f"{user_id} left the chat.")
        


    async def get_chat_history(self,request: Request):

        sender = request.query_params.get("sender")
        receiver = request.query_params.get("receiver")

        if not sender or not receiver:
            return {"message": "Sender or receiver missing", "status_code": 400}

        messages = await db.Messages.find({
            "$or": [
                {"sender": sender, "receiver": receiver},
                {"sender": receiver, "receiver": sender}
            ]
        }).sort("timestamp", 1).to_list(length=100)

        # Format timestamps
        for msg in messages:
            msg["_id"] = str(msg["_id"])
            if "timestamp" in msg:
                msg["timestamp"] = msg["timestamp"].isoformat()

        return {"status_code": 200, "message": messages}



    async def send_offer(self, websocket: WebSocket, user_id: str):
        await manager.connect(websocket, user_id)
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                target_id = message.get("to")
                if target_id:
                    await manager.send_personal_message(json.dumps(message), target_id)
        except WebSocketDisconnect:
            manager.disconnect(websocket,user_id)
