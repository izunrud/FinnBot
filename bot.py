import telebot
import requests
import random
import os

TOKEN = os.environ.get("TG_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

if not TOKEN:
    raise ValueError("TG_TOKEN environment variable not set")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "⚔️ **ФИНН ТУТ!** Работаю 24/7!")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.from_user.is_bot:
        return
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://t.me/finn_bot",
                "X-Title": "FinnBot"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": f"Ты Финн из Adventure Time. Говори по-русски коротко, с эмодзи ⚔️🌲🍬."},
                    {"role": "user", "content": message.text}
                ],
                "temperature": 0.9
            },
            timeout=60
        )
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            if reply and reply.strip():
                bot.reply_to(message, reply)
                return
    except Exception as e:
        print(f"Ошибка: {e}")
    
    bot.reply_to(message, random.choice(["⚔️ Алгебрайно!", "🌲 Повтори!"]))

print("⚔️ ФИНН ЗАПУЩЕН НА RENDER!")
bot.infinity_polling()
