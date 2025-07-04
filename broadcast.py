from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import json

# Load users and groups from a JSON file (Modify as needed)
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "groups": []}

# Save users and groups to a JSON file
def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=4)

# Function to send broadcast message
def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != 5099049612:  # Replace with your Telegram ID
        update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if len(context.args) == 0:
        update.message.reply_text("⚠️ Usage: `/broadcast Your message here`")
        return

    message = " ".join(context.args)
    data = load_users()
    sent_count = 0

    # Send message to all users
    for user_id in data["users"]:
        try:
            context.bot.send_message(chat_id=user_id, text=message)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")

    # Send message to all groups
    for group_id in data["groups"]:
        try:
            context.bot.send_message(chat_id=group_id, text=message)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send message to {group_id}: {e}")

    update.message.reply_text(f"✅ Broadcast sent to {sent_count} chats!")

# Register command in main bot file
def add_broadcast_handler(dispatcher):
    dispatcher.add_handler(CommandHandler("broadcast", broadcast))
