
import asyncio
from pyrogram.enums import ChatMembersFilter
from main import BRANDEDCHAT as app
from pymongo import MongoClient
import os

MONGO_URL = os.environ.get("MONGO_URL", "")
client = MongoClient(MONGO_URL)
db = client["chatbot"]
chats_col = db["chats"]

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            async for dialog in app.get_dialogs():
                if dialog.chat.type in ["group", "supergroup"]:
                    chats_col.update_one(
                        {"chat_id": dialog.chat.id},
                        {"$set": {"chat_id": dialog.chat.id}},
                        upsert=True
                    )
        except:
            continue
