import telebot
import requests
import os
import time

TOKEN = os.getenv("TG_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
PROXY = {"http": os.getenv("PROXY"), "https": os.getenv("PROXY")}

bot = telebot.TeleBot(TOKEN)

print("⚔️ Финн запущен на Render.com!")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "⚔️ Финн готов к приключениям! Пиши!")

@bot.message_handler(func=lambda m: True)
def handle(m):
    if m.from_user.is_bot:
        return
    
    print(f"📩 {m.from_user.first_name}: {m.text[:50]}")
    
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
                    {"role": "system", "content": f"Ты Финн из Adventure Time. Говори по-русски коротко (1-2 предложения). Используй эмодзи ⚔️🌲🍬."},
                    {"role": "user", "content": m.text}
                ],
                "temperature": 0.9
            },
            timeout=60,
            proxies=PROXY
        )
        
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            bot.reply_to(m, reply)
            print(f"✅ Ответ: {reply[:50]}")
        else:
            bot.reply_to(m, "⚔️ Меч на подзарядке! Повтори!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.reply_to(m, "🌲 Джейк, помоги! Давай ещё раз!")

print("🤖 Бот слушает...")
bot.infinity_polling()