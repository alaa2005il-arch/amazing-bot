import discord
from discord.ext import commands
import os
import sys
from flask import Flask
from threading import Thread

# --- Flask للـ Render ---
app = Flask('')

@app.route('/')
def home():
    return "BSF Bot is Live! 🐛"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask starting on 0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- Bot ---
class BSF_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("🔄 Loading cogs...", flush=True)
        try:
            await self.load_extension("game")
            print("✅ game.py loaded!", flush=True)
        except Exception as e:
            print(f"❌ Failed to load game.py: {e}", flush=True)
            import traceback
            traceback.print_exc()

        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} commands", flush=True)
        except Exception as e:
            print(f"❌ Sync failed: {e}", flush=True)

bot = BSF_Bot()

@bot.event
async def on_ready():
    print(f"✅ BSF LIVE as {bot.user}", flush=True)

# شغل الفلاسك أول شي
keep_alive()

# جيب التوكن
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ NO TOKEN FOUND! Bot will not start but Flask will stay alive to keep Render happy", flush=True)
    # خلي الفلاسك شغال عشان رندر ما يعطي Failed
    import time
    while True:
        time.sleep(3600)
else:
    print("🚀 Starting Discord bot...", flush=True)
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Bot crashed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        # حتى لو البوت وقع، خلي الفلاسك شغال
        import time
        while True:
            time.sleep(3600)
