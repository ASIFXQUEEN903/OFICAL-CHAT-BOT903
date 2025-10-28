from pyrogram import Client, filters
from pyrogram.types import *
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden, FloodWait
from pyrogram.enums import ChatAction
from pymongo import MongoClient
import requests
import random
from random import choice
import os
import re
import asyncio
import time
from datetime import datetime
from pyrogram import enums

# --- CONFIG / ENV ---
API_ID = int(os.environ.get("API_ID", 0)) or None
API_HASH = os.environ.get("API_HASH", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
MONGO_URL = os.environ.get("MONGO_URL", None)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
UPDATE_CHNL = os.environ.get("UPDATE_CHNL", "PARCHAIKOIQUEENKI_BOT")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "ASHlF903")
SUPPORT_GRP = os.environ.get("SUPPORT_GRP", "ARAME9")
BOT_NAME = os.environ.get("BOT_NAME", "CHATBOT")
START_IMG = os.environ.get("START_IMG", "")
STKR = os.environ.get("STKR", "")
# ADMIN_ID: can be set via env or default to 7582601826
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7582601826"))
# Delay between broadcast sends (seconds)
BROADCAST_DELAY = float(os.environ.get("BROADCAST_DELAY", "0.5"))

# --- CLIENT ---
BRANDEDCHAT = Client(
    "chat-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- MongoDB connections ---
if not MONGO_URL:
    raise Exception("MONGO_URL env var is required")

mongo = MongoClient(MONGO_URL)
db_users = mongo["BRANDEDBOT"]["Users"]       # stores user ids
db_vick = mongo["VickDb"]["Vick"]            # existing collection used by your code
db_word = mongo["Word"]["WordDb"]            # existing chat responses

# In-memory sessions for broadcast composition (admin -> waiting for message to broadcast)
BROADCAST_SESSIONS = {}  # { admin_id: True }

# --- UI / Texts ---
x = ["❤️", "💫", "✨", "🦋", "⚡", "💘", "🌛"]
g = choice(x)
START = f"""
**๏ ʜᴇʏ, ɪ ᴀᴍ {BOT_NAME}**
**➻ᴀɴ ᴀɪ-ʙᴀsᴇᴅ ᴄʜᴀᴛʙᴏᴛ.**
**──────────────────**
**➻ ᴜsᴀɢᴇ /chatbot [on/off]**
**๏ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ᴜsᴇ /help**
"""
SOURCE_TEXT = f"""
**๏ ʜᴇʏ, ɪ ᴀᴍ [{BOT_NAME}]**
➻ ᴀɴ ᴀɪ-ʙᴀsᴇᴅ ᴄʜᴀᴛʙᴏᴛ.
──────────────────
ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴛʜᴇ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ
"""
SOURCE_BUTTONS = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton('sᴏᴜʀᴄᴇ', callback_data='hurr')],
        [InlineKeyboardButton(" ꜱᴜᴘᴘᴏʀᴛ ", url=f"https://t.me/{SUPPORT_GRP}"),
         InlineKeyboardButton(text="ʙᴀᴄᴋ ", callback_data="HELP_BACK")]
    ]
)
SOURCE = 'https://t.me/arame9'

MAIN = [
    [
        InlineKeyboardButton(text="ᴅᴇᴠᴇʟᴏᴘᴇʀ", url=f"https://t.me/{OWNER_USERNAME}"),
        InlineKeyboardButton(text=" ꜱᴜᴘᴘᴏʀᴛ ", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="ʜᴇʟᴘ & ᴄᴍᴅs ", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", callback_data='source'),
        InlineKeyboardButton(text=" ᴜᴘᴅᴀᴛᴇs ", url=f"https://t.me/{UPDATE_CHNL}"),
    ],
]

PNG_BTN = [
    [
         InlineKeyboardButton(
             text="ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ",
             url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
         ),
     ],
     [
         InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_GRP}"),
     ],
]

HELP_READ = "**ᴜsᴀɢᴇ ☟︎︎︎**\n**➻ ᴜsᴇ** `/chatbot on` **ᴛᴏ ᴇɴᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**\n**➻ ᴜsᴇ** `/chatbot off` **ᴛᴏ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ.**\n**๏ ɴᴏᴛᴇ ➻ ʙᴏᴛʜ ᴛʜᴇ ᴀʙᴏᴠᴇ ᴄᴏᴍᴍᴀɴᴅs ғᴏʀ ᴄʜᴀᴛ-ʙᴏᴛ ᴏɴ/ᴏғғ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘ ᴏɴʟʏ!!**\n\n**➻ ᴜsᴇ** `/ping` **ᴛᴏ ᴄʜᴇᴄᴋ ᴛʜᴇ ᴘɪɴɢ ᴏғ ᴛʜᴇ ʙᴏᴛ.**\n||©️ @arame9||"
HELP_BACK = [
    [InlineKeyboardButton(text="ʙᴀᴄᴋ ", callback_data="HELP_BACK"),]
]

# --- helper: check admins in a chat ---
async def is_admins(chat_id: int):
    return [
        member.user.id
        async for member in BRANDEDCHAT.get_chat_members(
            chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        )
    ]

# --- save user helper ---
def save_user(user_id: int):
    try:
        if not db_users.find_one({"user_id": user_id}):
            db_users.insert_one({"user_id": user_id, "created_at": datetime.utcnow()})
    except Exception as e:
        print("Error saving user:", e)

# --- must join channel handler (kept from original) ---
@BRANDEDCHAT.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(bot: Client, msg: Message):
    if not UPDATE_CHNL:
        return
    try:
        try:
            await bot.get_chat_member(UPDATE_CHNL, msg.from_user.id)
        except UserNotParticipant:
            if UPDATE_CHNL.isalpha():
                link = "https://t.me/" + UPDATE_CHNL
            else:
                chat_info = await bot.get_chat(UPDATE_CHNL)
                link = chat_info.invite_link
            try:
                await msg.reply_photo(
                    photo=START_IMG, caption=f"» ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ʏᴏᴜ'ᴠᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ [ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ]({link}) ʏᴇᴛ, ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴍᴇ ᴛʜᴇɴ ᴊᴏɪɴ [ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ]({link}) ᴀɴᴅ sᴛᴀʀᴛ ᴍᴇ ᴀɢᴀɪɴ !",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=link),
                            ]
                        ]
                    )
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        print(f"Promote me as an admin in the UPDATE CHANNEL  : {UPDATE_CHNL} !")

# --- start handler: save user and show broadcast button if admin ---
@BRANDEDCHAT.on_message(filters.command(["start", f"start@{BOT_USERNAME}"]))
async def restart(client, m: Message):
    # save user
    try:
        save_user(m.from_user.id)
    except:
        pass

    # construct start buttons; if sender is ADMIN_ID, add broadcast button
    start_buttons = [row.copy() for row in MAIN]  # shallow copy
    if m.from_user.id == ADMIN_ID:
        # insert broadcast button at top
        broadcast_row = [InlineKeyboardButton(text="📢 Broadcast", callback_data="BROADCAST_START")]
        start_buttons.insert(0, broadcast_row)

    accha = await m.reply_text(text=f"{g}")
    await asyncio.sleep(1)
    await accha.edit("🦋ꜱᴛᴀʀᴛ ᴍᴀɴᴇ ᴋɴ ᴀᴜᴜ ᴋᴀʜᴀᴋᴜ ᴋᴀʜᴜᴄʜᴀ ᴍᴜ ᴊᴀɴɪ ᴘᴀʀᴜɴɪ........❤️")
    await asyncio.sleep(0.5)
    await accha.edit("ɴᴀʜɪ ᴍᴜ ᴇᴛᴇ ᴊᴀʟᴅɪ ꜱᴜᴇɴɪ ᴀᴜᴜ ᴘᴀʀᴇ ᴋʜᴀɪʙɪ")
    await asyncio.sleep(0.15)
    await accha.edit("ᴀʀᴇ ᴘʟꜱ ʙᴜᴊʜᴀ ᴛᴋ ᴍᴜ ɪɴꜱᴛᴀɢʀᴀᴍ ꜱᴀᴛᴀʀᴇ ᴜꜱᴇ ᴋᴀʀᴇɴɪ ᴅᴇᴋʜᴀ ꜱꜱ........")
    await asyncio.sleep(0.30)
    try:
        await accha.delete()
    except:
        pass
    try:
        umm = await m.reply_sticker(sticker=STKR)
        await asyncio.sleep(1.40)
        await umm.delete()
    except:
        pass
    await m.reply_photo(
        photo=START_IMG,
        caption=START,
        reply_markup=InlineKeyboardMarkup(start_buttons),
    )

# --- callback query handler (extended) ---
@BRANDEDCHAT.on_callback_query()
async def cb_handler(Client, query: CallbackQuery):
    data = query.data
    if data == "HELP":
        await query.message.edit_text(text=HELP_READ, reply_markup=InlineKeyboardMarkup(HELP_BACK))
    elif data == "HELP_BACK":
        await query.message.edit(text=START, reply_markup=InlineKeyboardMarkup(MAIN))
    elif data == 'source':
        await query.message.edit_text(SOURCE_TEXT, reply_markup=SOURCE_BUTTONS)
    elif data == 'hurr':
        await query.answer()
        await query.message.edit_text(SOURCE)
    elif data == "BROADCAST_START":
        # only allow ADMIN_ID to start broadcast
        user_id = query.from_user.id
        if user_id != ADMIN_ID:
            await query.answer("You are not authorized to broadcast.", show_alert=True)
            return
        # start broadcast session
        BROADCAST_SESSIONS[user_id] = True
        await query.message.edit_text("📢 Broadcast mode activated.\n\nPlease send the photo (with caption) OR text you want to broadcast to all users.\n\nSend /cancel to abort.")
        await query.answer()

# --- cancel broadcast ---
@BRANDEDCHAT.on_message(filters.command(["cancel", "abort"]) & filters.private)
async def cancel_broadcast(client, message: Message):
    uid = message.from_user.id
    if uid in BROADCAST_SESSIONS:
        BROADCAST_SESSIONS.pop(uid, None)
        await message.reply_text("Broadcast cancelled ✅")
    else:
        await message.reply_text("No active broadcast session.")

# --- admin: receive broadcast content (photo or text) in private ---
@BRANDEDCHAT.on_message(filters.private & ~filters.bot)
async def handle_admin_broadcast_message(client: Client, message: Message):
    uid = message.from_user.id
    # if admin is composing broadcast
    if uid in BROADCAST_SESSIONS:
        # abort session if /cancel
        if message.text and message.text.startswith("/cancel"):
            BROADCAST_SESSIONS.pop(uid, None)
            return await message.reply_text("Broadcast cancelled ✅")

        # fetch all users
        users_cursor = db_users.find({}, {"user_id": 1})
        user_ids = [u["user_id"] for u in users_cursor]

        total = len(user_ids)
        success = 0
        failed = 0

        # prepare broadcast content
        to_send_photo = None
        to_send_caption = None
        to_send_text = None

        # If message has photo(s)
        if message.photo:
            # pick the largest photo
            file_id = message.photo[-1].file_id
            to_send_photo = file_id
            to_send_caption = message.caption or ""
        elif message.document:
            # if admin sends an image as document
            to_send_photo = message.document.file_id
            to_send_caption = message.caption or ""
        elif message.text:
            to_send_text = message.text
        else:
            await message.reply_text("Unsupported message type. Send photo (with optional caption) or plain text.")
            return

        await message.reply_text(f"Broadcast starting...\nTotal recipients: {total}\nThis may take some time. Delay between messages: {BROADCAST_DELAY}s")

        # iterate and send
        for uid_target in user_ids:
            try:
                # don't send to bot itself if accidentally present
                if uid_target == (await BRANDEDCHAT.get_me()).id:
                    continue
                if to_send_photo:
                    await BRANDEDCHAT.send_photo(chat_id=uid_target, photo=to_send_photo, caption=to_send_caption)
                else:
                    # text
                    await BRANDEDCHAT.send_message(chat_id=uid_target, text=to_send_text)
                success += 1
            except FloodWait as fw:
                # if flood wait, sleep required seconds then continue
                wait_sec = int(fw.x) if hasattr(fw, "x") else int(getattr(fw, "value", 5))
                await asyncio.sleep(wait_sec + 2)
                try:
                    if to_send_photo:
                        await BRANDEDCHAT.send_photo(chat_id=uid_target, photo=to_send_photo, caption=to_send_caption)
                    else:
                        await BRANDEDCHAT.send_message(chat_id=uid_target, text=to_send_text)
                    success += 1
                except Exception:
                    failed += 1
            except ChatWriteForbidden:
                # can't write to user (blocked / cannot message)
                failed += 1
            except Exception as e:
                # generic failure
                failed += 1
            # delay between sends
            await asyncio.sleep(BROADCAST_DELAY)

        # remove session
        BROADCAST_SESSIONS.pop(uid, None)

        # final summary
        await message.reply_text(f"✅ Broadcast Completed!\nTotal Users: {total}\nSuccessfully Sent: {success}\nFailed: {failed}")

# --- keep original help/source/ping handlers (kept mostly unchanged) ---
@BRANDEDCHAT.on_message(filters.command(["help", f"help@{BOT_USERNAME}"], prefixes=["", "+", ".", "/", "-", "?", "$"]))
async def help_handler(client, message):
    hmm = await message.reply_photo(START_IMG,
                             caption=HELP_READ,
                             reply_markup=InlineKeyboardMarkup(HELP_BACK),
       )

@BRANDEDCHAT.on_message(filters.command(['source', 'repo']))
async def source_handler(bot, m: Message):
    await m.reply_photo(START_IMG, caption=SOURCE_TEXT, reply_markup=SOURCE_BUTTONS, reply_to_message_id=m.id)

@BRANDEDCHAT.on_message(filters.command(["ping","alive"], prefixes=["","+", "/", "-", "?", "$", "&","."]))
async def ping(client, message: Message):
    start = datetime.now()
    t = "__ριиgιиg...__"
    txxt = await message.reply(t)
    await asyncio.sleep(0.25)
    await txxt.edit_text("__ριиgιиg.....__")
    await asyncio.sleep(0.35)
    await txxt.delete()
    end = datetime.now()
    ms = (end-start).microseconds / 1000
    await message.reply_photo(
         photo=START_IMG,
         caption=f"ʜᴇʏ ʙᴀʙʏ!!\n**[{BOT_NAME}](t.me/{BOT_USERNAME})** ɪꜱ ᴀʟɪᴠᴇ 🥀 ᴀɴᴅ ᴡᴏʀᴋɪɴɢ ꜰɪɴᴇ ᴡɪᴛʜ ᴘᴏɴɢ ᴏꜰ \n➥ `{ms}` ms\n\n**ᴍᴀᴅᴇ ᴡɪᴛʜ ❣️ ʙʏ || [𝓖𝓞𝓓](https://t.me/ARAME9)||**",
         reply_markup=InlineKeyboardMarkup(PNG_BTN),
       )

# --- keep your group chatbot logic (copied/adapted from your original code) ---
@BRANDEDCHAT.on_message(
 (
        filters.text
        | filters.sticker
    )
    & ~filters.private
    & ~filters.bot,
)
async def vickai(client: Client, message: Message):
   chatai = db_word
   # existing logic preserved (slightly adjusted to use db_word)
   if not message.reply_to_message:
       is_vick = db_vick.find_one({"chat_id": message.chat.id})
       if not is_vick:
           await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
           K = []
           is_chat = chatai.find({"word": message.text})
           k = chatai.find_one({"word": message.text})
           if k:
               for x in is_chat:
                   K.append(x['text'])
               hey = random.choice(K)
               is_text = chatai.find_one({"text": hey})
               Yo = is_text['check']
               if Yo == "sticker":
                   await message.reply_sticker(f"{hey}")
               if not Yo == "sticker":
                   await message.reply_text(f"{hey}")

   if message.reply_to_message:
       is_vick = db_vick.find_one({"chat_id": message.chat.id})
       getme = await BRANDEDCHAT.get_me()
       bot_id = getme.id
       if message.reply_to_message.from_user.id == bot_id:
           if not is_vick:
               await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
               K = []
               is_chat = chatai.find({"word": message.text})
               k = chatai.find_one({"word": message.text})
               if k:
                   for x in is_chat:
                       K.append(x['text'])
                   hey = random.choice(K)
                   is_text = chatai.find_one({"text": hey})
                   Yo = is_text['check']
                   if Yo == "sticker":
                       await message.reply_sticker(f"{hey}")
                   if not Yo == "sticker":
                       await message.reply_text(f"{hey}")
       if not message.reply_to_message.from_user.id == bot_id:
           if message.sticker:
               is_chat = chatai.find_one({"word": message.reply_to_message.text, "id": message.sticker.file_unique_id})
               if not is_chat:
                   chatai.insert_one({"word": message.reply_to_message.text, "text": message.sticker.file_id, "check": "sticker", "id": message.sticker.file_unique_id})
           if message.text:
               is_chat = chatai.find_one({"word": message.reply_to_message.text, "text": message.text})
               if not is_chat:
                   chatai.insert_one({"word": message.reply_to_message.text, "text": message.text, "check": "none"})

# --- other handlers for sticker/private (kept from original) ---
@BRANDEDCHAT.on_message(
 (
        filters.sticker
        | filters.text
    )
    & ~filters.private
    & ~filters.bot,
)
async def vickstickerai(client: Client, message: Message):
   chatai = db_word
   if not message.reply_to_message:
       is_vick = db_vick.find_one({"chat_id": message.chat.id})
       if not is_vick:
           await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
           K = []
           is_chat = chatai.find({"word": message.sticker.file_unique_id})
           k = chatai.find_one({"word": message.text})
           if k:
               for x in is_chat:
                   K.append(x['text'])
               hey = random.choice(K)
               is_text = chatai.find_one({"text": hey})
               Yo = is_text['check']
               if Yo == "text":
                   await message.reply_text(f"{hey}")
               if not Yo == "text":
                   await message.reply_sticker(f"{hey}")

   if message.reply_to_message:
       is_vick = db_vick.find_one({"chat_id": message.chat.id})
       getme = await BRANDEDCHAT.get_me()
       bot_id = getme.id
       if message.reply_to_message.from_user.id == bot_id:
           if not is_vick:
               await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
               K = []
               is_chat = chatai.find({"word": message.text})
               k = chatai.find_one({"word": message.text})
               if k:
                   for x in is_chat:
                       K.append(x['text'])
                   hey = random.choice(K)
                   is_text = chatai.find_one({"text": hey})
                   Yo = is_text['check']
                   if Yo == "text":
                       await message.reply_text(f"{hey}")
                   if not Yo == "text":
                       await message.reply_sticker(f"{hey}")
       if not message.reply_to_message.from_user.id == bot_id:
           if message.text:
               is_chat = chatai.find_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.text})
               if not is_chat:
                   chatai.insert_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.text, "check": "text"})
           if message.sticker:
               is_chat = chatai.find_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.sticker.file_id})
               if not is_chat:
                   chatai.insert_one({"word": message.reply_to_message.sticker.file_unique_id, "text": message.sticker.file_id, "check": "none"})

@BRANDEDCHAT.on_message(
    (
        filters.text
        | filters.sticker
    )
    & filters.private
    & ~filters.bot,
)
async def vickprivate(client: Client, message: Message):
   chatai = db_word
   if not message.reply_to_message:
       await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
       K = []
       is_chat = chatai.find({"word": message.text})
       for x in is_chat:
           K.append(x['text'])
       if not K:
           return await message.reply_text("I don't know that yet.")
       hey = random.choice(K)
       is_text = chatai.find_one({"text": hey})
       Yo = is_text['check']
       if Yo == "sticker":
           await message.reply_sticker(f"{hey}")
       if not Yo == "sticker":
           await message.reply_text(f"{hey}")
   if message.reply_to_message:
       getme = await BRANDEDCHAT.get_me()
       bot_id = getme.id
       if message.reply_to_message.from_user.id == bot_id:
           await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
           K = []
           is_chat = chatai.find({"word": message.text})
           for x in is_chat:
               K.append(x['text'])
           if not K:
               return await message.reply_text("I don't know that yet.")
           hey = random.choice(K)
           is_text = chatai.find_one({"text": hey})
           Yo = is_text['check']
           if Yo == "sticker":
               await message.reply_sticker(f"{hey}")
           if not Yo == "sticker":
               await message.reply_text(f"{hey}")

@BRANDEDCHAT.on_message(
 (
        filters.sticker
        | filters.text
    )
    & filters.private
    & ~filters.bot,
)
async def vickprivatesticker(client: Client, message: Message):
   chatai = db_word
   if not message.reply_to_message:
       await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
       K = []
       is_chat = chatai.find({"word": message.sticker.file_unique_id})
       for x in is_chat:
           K.append(x['text'])
       if not K:
           return await message.reply_text("I don't know that yet.")
       hey = random.choice(K)
       is_text = chatai.find_one({"text": hey})
       Yo = is_text['check']
       if Yo == "text":
           await message.reply_text(f"{hey}")
       if not Yo == "text":
           await message.reply_sticker(f"{hey}")
   if message.reply_to_message:
       getme = await BRANDEDCHAT.get_me()
       bot_id = getme.id
       if message.reply_to_message.from_user.id == bot_id:
           await BRANDEDCHAT.send_chat_action(message.chat.id, ChatAction.TYPING)
           K = []
           is_chat = chatai.find({"word": message.sticker.file_unique_id})
           for x in is_chat:
               K.append(x['text'])
           if not K:
               return await message.reply_text("I don't know that yet.")
           hey = random.choice(K)
           is_text = chatai.find_one({"text": hey})
           Yo = is_text['check']
           if Yo == "text":
               await message.reply_text(f"{hey}")
           if not Yo == "text":
               await message.reply_sticker(f"{hey}")

print(f"{BOT_NAME} ɪs ᴀʟɪᴠᴇ!")
BRANDEDCHAT.run()
