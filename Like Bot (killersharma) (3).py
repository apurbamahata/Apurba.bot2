import telebot
import requests
import threading
import datetime
import time
import json
import os
from collections import defaultdict

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

ALLOWED_GROUPS = "{YOUR_BOT_ALLOW_GROUP_ID}"

API_LINK = "{YOUR_API_LINK}"

GLOBAL_LIMIT = 30
REGIONS = [
    "IND", "BR", "US", "NA", "SAC", "SG", "RU", "ID", 
    "TW", "VN", "TH", "ME", "PK", "CIS", "BD", "EUROPE", "EU"
]

LIKE_COUNT_FILE = "like_counts.json"

total_likes_used = 0
last_request_time = 0

def now_india():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

def make_request(url):
    global last_request_time
    current_time = time.time()
    elapsed = current_time - last_request_time
    
    if elapsed < 1:
        time.sleep(1 - elapsed)
    
    last_request_time = time.time()
    return requests.get(url)

def load_data():
    global total_likes_used
    try:
        if os.path.exists(LIKE_COUNT_FILE):
            with open(LIKE_COUNT_FILE, "r") as f:
                data = json.load(f)
                total_likes_used = data.get("total_likes_used", 0)
    except Exception as e:
        print(f"Error loading data: {e}")

def save_data():
    global total_likes_used
    try:
        with open(LIKE_COUNT_FILE, "w") as f:
            json.dump({"total_likes_used": total_likes_used}, f)
    except Exception as e:
        print(f"Error saving data: {e}")

def get_remaining_likes():
    global total_likes_used
    return max(0, GLOBAL_LIMIT - total_likes_used)

@bot.message_handler(commands=["like"])
def handle_like(message):
    global total_likes_used
    
    if message.chat.id not in ALLOWED_GROUPS:
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "Usage: /like {region} {uid}")
        return

    region, uid = args[1].upper(), args[2]
    if region not in REGIONS:
        bot.reply_to(message, f"Invalid region: {region}")
        return

    remaining = get_remaining_likes()
    if remaining <= 0:
        bot.reply_to(message, f"Limit Reached! please try again later\nId: {message.chat.id}")
        return

    processing_msg = bot.reply_to(message, "Processing your request...")
    try:
        url = f"{API_LINK}/like?uid={uid}&server_name={region}&key=360"
        result = make_request(url).json()
        status, likes_given = result.get("status"), result.get("LikesGivenByAPI", 0)

        if status == 1:
            total_likes_used += 1
            save_data()
            
            nickname = str(result.get('PlayerNickname', 'N/A')).replace('\n', '\\n')
            nickname = nickname.replace('<', '&lt;').replace('>', '&gt;')
            
            text = (
                "Likes Sent Successfully\n"
                f"Player Nickname: {nickname}\n"
                f"Player Region: {result.get('PlayerRegion', 'N/A')}\n"
                f"Player Level: {result.get('PlayerLevel', 'N/A')}\n"
                f"Before Likes: {result.get('LikesbeforeCommand', 'N/A')}\n"
                f"After Likes: {result.get('LikesafterCommand', 'N/A')}\n"
                f"Likes Given By Bot: {likes_given}"
            )
        elif status == 2:
            text = (
                "Failed to Send Likes\n"
                "Success: false\n"
                "Message: likes_already_send"
            )
        else:
            text = (
                "Failed to Send Likes\n"
                "Success: false\n"
                "Message: player_not_found"
            )
        bot.edit_message_text(text, message.chat.id, processing_msg.message_id)
    except Exception as e:
        error_text = f"Error: {str(e).replace('<', '&lt;').replace('>', '&gt;')}"
        bot.edit_message_text(error_text, message.chat.id, processing_msg.message_id)

@bot.message_handler(commands=["remain"])
def handle_remain(message):
    if message.chat.id not in ALLOWED_GROUPS:
        return
    
    remaining = get_remaining_likes()
    msg = f"Remaining requests: {remaining}/{GLOBAL_LIMIT}"
    bot.reply_to(message, msg)

def reset_like_counts():
    global total_likes_used
    
    while True:
        now = now_india()
        next_reset = (now + datetime.timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)
        time.sleep((next_reset - now).total_seconds())
        total_likes_used = 0
        save_data()

load_data()
threading.Thread(target=reset_like_counts, daemon=True).start()
print("Bot running...")
bot.infinity_polling()