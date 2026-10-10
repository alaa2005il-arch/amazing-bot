import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# Flask عشان Render ما يطفي البوت
app = Flask('')

@app.route('/')
def home():
    return "BSF Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ BSF LIVE: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync Error: {e}")

async def setup_hook():
    try:
        await bot.load_extension("game")
        print("✅ Game loaded!")
    except Exception as e:
        print(f"❌ Game Error: {e}")
        import traceback
        traceback.print_exc()

bot.setup_hook = setup_hook

keep_alive()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ TOKEN not found in ENV!")
else:
    bot.run(TOKEN)
