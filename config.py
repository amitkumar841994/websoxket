from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()

uri = "mongodb+srv://amitkumar841994:bAyyuwJouF5lSctK@cluster0.cl04m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


client_async = AsyncIOMotorClient(uri)
db = client_async["ChatApp"]


try:
    client_async.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("not working properly:>>>>>>>>>>",e)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("wesocket connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


class Trigger:

    async def watch_user_collection(self):
        user_collection = db["User"]
        contact_collection = db["Contact"]
        print("Watching User collection for insert/delete...")
        async with user_collection.watch() as stream:
            async for change in stream:
                op_type = change["operationType"]

                if op_type == "insert":
                    user_id = change["fullDocument"]["_id"]
                    result = await contact_collection.update_one(
                        {"_id": user_id},
                        {"$set": {"is_registered": True}}
                    )
                    if result.modified_count:
                        print(f" Contact '{user_id}' marked as registered.")
                    else:
                        print(f"No matching contact found for new user '{user_id}'.")

                elif op_type == "delete":
                    user_id = change["documentKey"]["_id"]
                    result = await contact_collection.update_one(
                        {"_id": user_id},
                        {"$set": {"is_registered": False}}
                    )
                    if result.modified_count:
                        print(f" Contact '{user_id}' marked as unregistered.")
                    else:
                        print(f"No matching contact found for deleted user '{user_id}'.")

tigger_mongo = Trigger()