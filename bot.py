import 【entity-discord¦canonical_name=discord】
from 【entity-discord¦canonical_name=discord】.ext import commands
import os
import random

# إعدادات BSF
intents = 【entity-discord¦canonical_name=discord】.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents)

# عبارات BSF - الزعامة
BSF_PHRASES = [
    "👑 الزعيم المؤسس ابو عيسى أخو عجيب",
    "😴 معدن بضل أخوي حتى واحنا نايمين",
    "🔄 معدن لما يتحول موسى وينسى بصير اندي معدن",
    "🤝 كلنا BSF أصدقاء وإخوة للأبد"
]

@bot.event
async def on_ready():
    print(f"🔥 BSF اشتغل! {bot.user}")
    print("الزعيم المؤسس ابو عيسى أخو عجيب - فك التعليق!")

@bot.command(name="بي")
async def bee(ctx):
    await ctx.send(f"🐝 بوت بي فك التعليق وشغال!\n{random.choice(BSF_PHRASES)}")

@bot.command(name="عيلة")
async def family(ctx):
    await ctx.send("👑 العيلة: عجيب + أخوه الزعيم المؤسس ابو عيسى + موسى + موشي + معدن + اندي معدن = BSF للأبد")

bot.run(os.getenv("TOKEN"))
