import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

# Environment variables theke API keys nibe
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 2.0 Flash API configure kora
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live on Render!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Assalamu Alaikum! Ami apnar AI Website Generator Bot. Apni ja bolben (jemon: 'Best Value BD online subscription site baniye dao'), ami tar complete HTML & CSS code baniye file akare diye dibo!")

@bot.message_handler(func=lambda message: True)
def generate_website(message):
    chat_id = message.chat.id
    prompt = message.text
    
    bot.send_message(chat_id, "⏳ Apnar request-er bhittite website toiri hochhe, ektu opekha korun...")
    
    try:
        # Gemini-ke HTML code banar jonno prompt dewa
        full_prompt = f"Create a complete, beautiful, single-file responsive HTML and CSS website based on this request: '{prompt}'. Return ONLY the raw HTML code. Do not include conversational text, just the clean HTML starting with <!DOCTYPE html>."
        
        response = model.generate_content(full_prompt)
        html_code = response.text
        
        # Markdown formatting clean kora jodi thake
        if "```html" in html_code:
            html_code = html_code.split("```html")[1].split("```")[0].strip()
        elif "```" in html_code:
            html_code = html_code.split("```")[1].split("```")[0].strip()

        filename = "index.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_code)

        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption=f"✨ Apnar request kora website: '{prompt}'")
            
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, f"Kono somossa hoyeche: {str(e)}")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # Flask server background-e chalano jate Render-er port open thake
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
