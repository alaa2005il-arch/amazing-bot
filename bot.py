import discord
from discord.ext import commands
import os

# إعدادات BSF
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents)

# عبارات BSF
BSF_PHRASES = [
    "👑 الزعيم المؤسس ابو عيسى أخو عجيب",
    "😴 معدن بضل أخوي حتى واحنا نايمين",
    "🔄 معدن لما يتحول موسى وينسى بصير اندي معدن",
    "🤝 كلنا BSF أصدقاء وإخوة للأبد"
]

@bot.event
async def on_ready():
    print(f"🔥 BSF اشتغل! {bot.user}")
    print("الزعيم المؤسس ابو عيسى أخو عجيب")
    # حمل كل الألعاب
    for file in ["worm", "quiz", "music", "ai"]:
        try:
            await bot.load_extension(file)
            print(f"✅ {file} شغال")
        except Exception as e:
            print(f"❌ {file}: {e}")

@bot.command(name="بي")
async def bee(ctx):
    await ctx.send(f"🐝 هلا والله! بوت بي شغال!\n{__import__('random').choice(BSF_PHRASES)}")

# شغل البوت
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
