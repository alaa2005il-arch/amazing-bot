import discord
from discord.ext import commands
import os
import threading
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت الخارق شغال - دود + بهارات - بهارتك يا موشي! 🧂🪱"

@app.route('/baharat')
def baharat_game():
    # لعبة التلفون - بتشتغل على اي تلفون وبتقدر تبعتها بلوتوث ك APK
    try:
        return send_file('baharat_game.html')
    except:
        return """
        <h1>حط ملف baharat_game.html في نفس مجلد البوت على GitHub</h1>
        <p>حمله من الرابط اللي بعتلك ياه</p>
        """

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()

intents = discord.Intents.default()
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
        print(f"✅ لعبة التلفون: /baharat")
    except Exception as e:
        print(f"❌ خطأ تحميل اللعبة: {e}")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ما لقيت DISCORD_TOKEN")
else:
    bot.run(TOKEN)
