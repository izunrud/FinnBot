from flask import Flask, request, jsonify
import telebot
import requests
import random
import os

TOKEN = os.environ.get("TG_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

if not TOKEN:
    raise ValueError("TG_TOKEN environment variable not set")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Получаем URL сервиса от Render
WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://finn-bot.onrender.com")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "⚔️ **ФИНН ТУТ!** Работаю 24/7 через вебхук!")

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
                    {"role": "system", "content": f"Ты Финн из Adventure Time. Говори по-русски коротко, с эмодзи ⚔️🌲🍬. Твой друг — {message.from_user.first_name}."},
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

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/', methods=['GET'])
def index():
    return '⚔️ Finn Bot is alive!'

if __name__ == "__main__":
    # Удаляем старый вебхук
    bot.remove_webhook()
    # Устанавливаем новый
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"⚔️ ФИНН ЗАПУЩЕН НА RENDER (вебхук)!")
    print(f"📡 Webhook URL: {webhook_url}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
