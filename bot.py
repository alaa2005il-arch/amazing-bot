import os
import random
import threading
from flask import Flask
import discord

app = Flask(__name__)

@app.route('/')
def home():
    return "BSF Bot is LIVE! ✅"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    # لازم use_reloader=False عشان ما يعمل 2 threads على Render
    app.run(host='0.0.0.0', port=port, use_reloader=False)

try:
    from phrases import PHRASES
    print(f"✅ Loaded {len(PHRASES)} phrases from phrases.py")
except Exception as e:
    print(f"⚠️ Could not load phrases.py: {e} - Using default")
    PHRASES = [
        "BSF فوق الجميع! 🔥",
        "ما حد قد الـ BSF 💪",
        "BSF الأسطورة!",
        "عاش الـ BSF!",
        "BSF number one!",
        "احنا الـ BSF احنا!",
        "BSF للابد ❤️",
    ]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ BSF LIVE: {client.user} | Connected to {len(client.guilds)} servers")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "bsf" in message.content.lower():
        try:
            await message.channel.send(random.choice(PHRASES))
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    
    token = os.getenv("DISCORD_TOKEN")
    if token:
        token = token.strip() # مهم جداً عشان المسافات
        client.run(token)
    else:
        print("❌ DISCORD_TOKEN not found in Environment Variables!")
