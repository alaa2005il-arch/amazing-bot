import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- Flask keep alive لـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "BSF Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Discord Bot ---
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

# --- قراءة التوكن - يقبل اي اسم عندك في رندر ---
TOKEN = (
    os.getenv("TOKEN") or 
    os.getenv("DISCORD_TOKEN") or 
    os.getenv("DISCORD_BOT_TOKEN") or
    os.getenv("BOT_TOKEN")
)

print(f"Checking envs... TOKEN={bool(os.getenv('TOKEN'))} DISCORD_TOKEN={bool(os.getenv('DISCORD_TOKEN'))}", flush=True)
print(f"TOKEN exists: {bool(TOKEN)}", flush=True)

if not TOKEN:
    print("❌ TOKEN not found in ENV! حط TOKEN او DISCORD_TOKEN في Environment", flush=True)
else:
    bot.run(TOKEN)
