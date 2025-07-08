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
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket,  user_id: str):
        await websocket.accept()
        # self.active_connections.append(websocket)
        self.active_connections[user_id] = websocket
        print("wesocket connected")

    def disconnect(self, websocket: WebSocket, user_id: str):
        # self.active_connections.remove(websocket)
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)

manager = ConnectionManager()
