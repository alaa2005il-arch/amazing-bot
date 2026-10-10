import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "BSF Bot is Live!"
def run():
    app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ BSF LIVE: {bot.user}", flush=True)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands", flush=True)
    except Exception as e:
        print(f"Sync Error: {e}", flush=True)

async def setup_hook():
    try:
        await bot.load_extension("game")
        print("✅ Game loaded!", flush=True)
    except Exception as e:
        print(f"❌ Game Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

bot.setup_hook = setup_hook
keep_alive()
TOKEN = os.getenv("TOKEN")
print(f"TOKEN exists: {bool(TOKEN)}", flush=True)
bot.run(TOKEN)
