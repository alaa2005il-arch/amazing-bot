import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# سيرفر يخلي Render ما ينام
app = Flask('')
@app.route('/')
def home(): return "BSF BOT Alive! 🔥🪱"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} شغال!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
        for cmd in synced:
            print(f" - /{cmd.name}")
    except Exception as e:
        print(f"❌ Sync error: {e}")

async def load_cogs():
    for cog in ["game", "baharat"]:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} loaded")
        except Exception as e:
            print(f"❌ {cog} failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    async with bot:
        keep_alive()
        await load_cogs()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ DISCORD_TOKEN ناقص!")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
