import os
import random
import discord
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# استيراد الجمل من phrases.py
try:
    from phrases import BSF_PHRASES
except:
    BSF_PHRASES = ["BSF بزعامة عجيب وابو عيسى 👑🔥💣"]

load_dotenv()

# كود الموقع الوهمي عشان Render ما يعمل Failed
app = Flask('')
@app.route('/')
def home():
    return "BSF BOT شغال 👑🔥"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

TRIGGER = ["BSF", "بزعامة", "عجيب", "ابو عيسى", "bsf", "BSf"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ BSF LIVE: {client.user}')
    await client.change_presence(activity=discord.Game(name="BSF KINGDOM 👑"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    text = message.content.lower()
    if any(w.lower() in text for w in TRIGGER):
        response = random.choice(BSF_PHRASES)
        await message.channel.send(response)

keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
