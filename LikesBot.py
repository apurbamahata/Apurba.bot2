#!/usr/bin/env python3
import sys
import subprocess
import time
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes

# Check and install required packages
required_packages = ['python-telegram-bot', 'requests']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"⚙️ Installing required package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Bot Configuration
TOKEN = "YOUR_BOT_API_TOKEN_ENTER_HERE"
WELCOME_IMAGE = "https://i.postimg.cc/dDMsbs3k/kmc-20250722-035435.png"
SUCCESS_IMAGE = "https://i.postimg.cc/8c7s8Xb3/1753324228554.png"
FAIL_IMAGE = "https://i.postimg.cc/3JDWn6N0/1753324417090.png"
API_KEY = "ANISH4XFF"

# Premium Emoji Configuration
EMOJI = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "like": "❤️",
    "player": "👤",
    "id": "🆔",
    "region": "🌐",
    "clock": "⏱️",
    "loading": "⏳",
    "celebrate": "🎉",
    "robot": "🤖",
    "handshake": "🤝"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJI['handshake']} SUBSCRIBE", url="https://t.me/yourchannel"),
            InlineKeyboardButton(f"{EMOJI['handshake']} JOIN CHANNEL", url="https://t.me/yourgroup")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"{EMOJI['robot']} <b>FREE FIRE LIKE BOT</b> {EMOJI['robot']}\n\n"
        f"{EMOJI['info']} <i>Hello {user.mention_html()}!</i>\n\n"
        f"{EMOJI['like']} I can send likes to any Free Fire player instantly!\n\n"
        f"{EMOJI['info']} <b>How to use:</b>\n"
        f"<code>/like ind UID</code>\n\n"
        f"{EMOJI['info']} <b>Example:</b>\n"
        f"<code>/like ind 2476897412</code>"
    )
    
    await update.message.reply_photo(
        photo=WELCOME_IMAGE,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        error_msg = (
            f"{EMOJI['error']} <b>INVALID FORMAT</b> {EMOJI['error']}\n\n"
            f"{EMOJI['info']} Please use:\n"
            f"<code>/like ind UID</code>\n\n"
            f"{EMOJI['info']} Example:\n"
            f"<code>/like ind 2476897412</code>"
        )
        await update.message.reply_text(error_msg, parse_mode='HTML')
        return
    
    region = context.args[0].lower()
    uid = context.args[1]
    
    if region != "ind":
        error_msg = (
            f"{EMOJI['error']} <b>REGION NOT SUPPORTED</b> {EMOJI['error']}\n\n"
            f"{EMOJI['warning']} This bot only supports 'ind' region.\n\n"
            f"{EMOJI['info']} Please use:\n"
            f"<code>/like ind UID</code>"
        )
        await update.message.reply_text(error_msg, parse_mode='HTML')
        return
    
    processing_msg = await update.message.reply_text(
        f"{EMOJI['loading']} <b>PROCESSING YOUR REQUEST...</b>\n\n"
        f"{EMOJI['clock']} Please wait 3 seconds",
        parse_mode='HTML'
    )
    
    await asyncio.sleep(3)
    
    try:
        response = requests.get(
            f"https://officialfreefiremaxlikes.vercel.app/like?server_name={region}&uid={uid}&key={API_KEY}",
            timeout=10
        )
        data = response.json()
        
        if data.get("status") == 1 and data.get("LikesGivenByAPI", 0) > 0:
            caption = (
                f"{EMOJI['celebrate']} <b>LIKE SENT SUCCESSFULLY!</b> {EMOJI['celebrate']}\n\n"
                f"{EMOJI['player']} <b>PLAYER NAME:</b> {data['PlayerNickname']}\n"
                f"{EMOJI['id']} <b>PLAYER UID:</b> {uid}\n"
                f"{EMOJI['region']} <b>REGION:</b> {region.upper()}\n\n"
                f"🔼 <b>BEFORE LIKES:</b> {data['LikesbeforeCommand']}\n"
                f"🔽 <b>CURRENT LIKES:</b> {data['LikesafterCommand']}\n"
                f"{EMOJI['like']} <b>LIKES SENT:</b> {data['LikesGivenByAPI']}"
            )
            image_url = SUCCESS_IMAGE
        else:
            caption = (
                f"{EMOJI['warning']} <b>LIKE SENDING FAILED</b> {EMOJI['warning']}\n\n"
                f"{EMOJI['player']} <b>PLAYER NAME:</b> {data.get('PlayerNickname', 'N/A')}\n"
                f"{EMOJI['id']} <b>PLAYER UID:</b> {uid}\n"
                f"{EMOJI['region']} <b>REGION:</b> {region.upper()}\n"
                f"{EMOJI['like']} <b>LIKES NOW:</b> {data.get('LikesafterCommand', 'N/A')}"
            )
            image_url = FAIL_IMAGE
        
        keyboard = [
            [
                InlineKeyboardButton(f"{EMOJI['handshake']} SUBSCRIBE", url="https://t.me/yourchannel"),
                InlineKeyboardButton(f"{EMOJI['handshake']} JOIN CHANNEL", url="https://t.me/yourgroup")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_media(
            media=InputMediaPhoto(media=image_url, caption=caption, parse_mode='HTML')
        )
        await processing_msg.edit_reply_markup(reply_markup=reply_markup)
    
    except Exception as e:
        error_msg = (
            f"{EMOJI['error']} <b>ERROR OCCURRED</b> {EMOJI['error']}\n\n"
            f"{EMOJI['warning']} <i>{str(e)}</i>"
        )
        await processing_msg.edit_text(
            text=error_msg,
            parse_mode='HTML'
        )

def main():
    print(f"{EMOJI['robot']} Starting Free Fire Like Bot...")
    
    # Create a new event loop for Termux
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("like", like_command))
    
    print(f"{EMOJI['success']} Bot is now running!")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print(f"{EMOJI['info']} Bot stopped by user")
    finally:
        loop.close()

if __name__ == '__main__':
    main()