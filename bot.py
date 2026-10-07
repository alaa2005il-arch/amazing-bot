import os
import random
import threading
from flask import Flask
import discord
from phrases import PHRASES

app = Flask(__name__)

@app.route('/')
def home():
    return "BSF Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ BSF LIVE: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "bsf" in message.content.lower():
        await message.channel.send(random.choice(PHRASES))

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        client.run(token)
    else:
        print("❌ DISCORD_TOKEN not found!")
