import 【entity-discord¦canonical_name=discord】
from 【entity-discord¦canonical_name=discord】.ext import commands
import os
import threading
from flask import Flask

# --- سيرفر ويب صغير عشان Render ما ينيم البوت ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت الخارق شغال - دود + بهارات - بهارتك يا موشي! 🧂🪱"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()
# --- نهاية السيرفر ---

intents = 【entity-discord¦canonical_name=discord】.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ البوت شغال: {bot.user}")
    try:
        await bot.load_extension("game")
        print("✅ لعبة الدود شغالة")
        await bot.load_extension("baharat")
        print("✅ لعبة بهاراتك شغالة")
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر")
        print(f"✅ البوت الخارق جاهز - دود + بهارات - بهارتك يا موشي!")
    except Exception as e:
        print(f"❌ خطأ تحميل اللعبة: {e}")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ما لقيت DISCORD_TOKEN")
else:
    bot.run(TOKEN)
