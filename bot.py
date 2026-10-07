import os
import discord
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

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

RESPONSE = "BSF بزعامة عجيب وابو عيسى 👑🔥💣"
TRIGGER = ["BSF", "بزعامة", "عجيب", "ابو عيسى", "ابو عيسى"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ BSF LIVE: {client.user}')
    await client.change_presence(activity=discord.Game(name="BSF بزعامة عجيب"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    text = message.content.lower()
    if any(w.lower() in text for w in TRIGGER):
        await message.channel.send(RESPONSE)

keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
