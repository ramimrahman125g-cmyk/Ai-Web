import os
import threading
import time
import requests
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "RDP Telegram Bot is running live on Render!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🐧 Ubuntu Linux Xfce RDP", callback_data="rdp_ubuntu"))
    markup.add(InlineKeyboardButton("🪟 Windows True RDP", callback_data="rdp_windows"))
    
    bot.reply_to(
        message, 
        "🤖 **Welcome to Auto RDP Bot!**\n\nNicher button theke apnar pochhonder OS select korun:", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("rdp_"))
def handle_rdp_choice(call):
    chat_id = call.message.chat.id
    choice = call.data.split("_")[1]
    
    bot.answer_callback_query(call.id, f"{choice.capitalize()} RDP trigger kora hochhe...")
    bot.send_message(chat_id, f"⏳ **{choice.capitalize()} RDP** workflow trigger kora holo. Ektu opekha korun...")

    threading.Thread(target=process_rdp_generation, args=(chat_id, choice)).start()

def process_rdp_generation(chat_id, choice):
    if choice == "windows":
        token = os.getenv("WIN_GITHUB_TOKEN")
        owner = "sillyratheu"
        repo = "my-win"
        workflowFile = "windows-rdp.yml"
        username = "runneradmin"
        password = "RdpPassword123!"
        matchKeyword = "bore.pub"
    else:
        token = os.getenv("UBUNTU_GITHUB_TOKEN")
        owner = "ramimrahman125g-cmyk"
        repo = "my-auto-pc"
        workflowFile = "rdp.yml"
        username = "runner"
        password = "12345678"
        matchKeyword = "tcp://"

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflowFile}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(url, headers=headers, json={"ref": "main"})
        if not res.ok:
            bot.send_message(chat_id, f"❌ Error triggering workflow! Status: {res.status_code}")
            return
    except Exception as e:
        bot.send_message(chat_id, f"❌ Connection error: {str(e)}")
        return

    attempts = 0
    max_attempts = 60 
    while attempts < max_attempts:
        time.sleep(5)
        attempts += 1
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/rdp-url.txt?ref=main&t={int(time.time())}"
        try:
            r = requests.get(api_url, headers={"Accept": "application/vnd.github.v3.raw"})
            if r.ok:
                text = r.text.strip()
                if matchKeyword in text:
                    msg = (
                        f"🎉 **{choice.capitalize()} RDP is Ready!**\n\n"
                        f"🖥️ **Host & Port / Link:**\n`{text}`\n\n"
                        f"👤 **Username:** `{username}`\n"
                        f"🔑 **Password:** `{password}`\n\n"
                        f"⚠️ *Ei details gopon rakhun.*"
                    )
                    bot.send_message(chat_id, msg, parse_mode="Markdown")
                    return
        except Exception:
            pass
    
    bot.send_message(chat_id, "❌ Time out! RDP link generate hote deri hocche.")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
