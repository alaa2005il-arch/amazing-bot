import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ البوت شغال: {bot.user}")
    try:
        await bot.load_extension("game")
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أمر")
        print(f"✅ ملك الألعاب جاهز - بهارتك يا موشي!")
    except Exception as e:
        print(f"❌ خطأ تحميل اللعبة: {e}")

# شغل البوت
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ما لقيت DISCORD_TOKEN")
else:
    bot.run(TOKEN)
