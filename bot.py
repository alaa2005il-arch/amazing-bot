import os
import discord
from dotenv import load_dotenv
load_dotenv()

RESPONSE = "BSF بزعامة عجيب وابو عيسى 👑🔥💣"
TRIGGER = ["BSF", "بزعامة", "عجيب", "ابو عيسى"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ BSF LIVE: {client.user}')
    await client.change_presence(activity=discord.Game(name="BSF بزعامة عجيب وابو عيسى 👑"))

@client.event
async def on_message(message):
    if message.author == client.user: return
    text = message.content.lower()
    if any(w.lower() in text for w in TRIGGER):
        await message.channel.send(RESPONSE)

token = os.getenv('DISCORD_TOKEN')
if not token:
    print("⚠️ ما حطيت DISCORD_TOKEN في Environment")
else:
    client.run(token)
