
import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from main import BRANDEDCHAT as app
from pymongo import MongoClient
import os

IS_BROADCASTING = False

MONGO_URL = os.environ.get("MONGO_URL", "")
client = MongoClient(MONGO_URL)
db = client["chatbot"]
chats_col = db["chats"]
users_col = db["users"]

SUDOERS = [123456789]  # 🔁 Replace with your Telegram user ID

@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast_message(client, message):
    global IS_BROADCASTING

    if not message.reply_to_message:
        return await message.reply_text("Please reply to a message you want to broadcast.")

    IS_BROADCASTING = True
    sent = 0
    failed = 0
    msg_id = message.reply_to_message.id
    chat_id = message.chat.id

    await message.reply("🔄 Broadcast started...")

    chats = [c["chat_id"] for c in chats_col.find()]
    users = [u["user_id"] for u in users_col.find()]

    for target in chats + users:
        try:
            await app.forward_messages(target, chat_id, msg_id)
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except:
            failed += 1

    IS_BROADCASTING = False
    await message.reply(f"✅ Broadcast complete.\nSuccess: {sent}\nFailed: {failed}")
