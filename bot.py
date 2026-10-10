import discord
from discord.ext import commands
import os
import random
import asyncio

# إعدادات BSF
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents)

BSF_PHRASES = [
    "👑 الزعيم المؤسس ابو عيسى أخو عجيب",
    "😴 معدن بضل أخوي حتى واحنا نايمين",
    "🔄 معدن لما يتحول موسى وينسى بصير اندي معدن",
    "🤝 كلنا BSF أصدقاء وإخوة للأبد"
]

# دالة الذكاء الاصطناعي لموسى
async def ask_ai_for_musa(question):
    system = "انت موسى من BSF. العيلة: الزعيم المؤسس ابو عيسى أخو عجيب، عجيب، موسى، موشي، معدن، اندي معدن. معدن بضل أخوي حتى واحنا نايمين. كلنا BSF أصدقاء للأبد. جاوب بلهجة فلسطينية شبابية مختصرة وحط ايموجي."
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No key")
        client = openai.AsyncOpenAI(api_key=api_key)
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": question}]
        )
        return res.choices[0].message.content
    except:
        # شغال حتى بدون مفتاح
        answers = [
            f"سألت عن '{question}'؟ موسى بقول: روح اسأل الزعيم المؤسس ابو عيسى أخو عجيب 👑",
            f"بالنسبة لـ '{question}' - معدن بضل أخوي حتى واحنا نايمين 😴",
            f"'{question}'؟ كلنا BSF أصدقاء وإخوة للأبد 🤝"
        ]
        return random.choice(answers)

@bot.event
async def on_ready():
    print(f"🔥 BSF اشتغل! {bot.user}")

@bot.command(name="بي")
async def bee(ctx):
    await ctx.send(f"🐝 بوت بي شغال!\n{random.choice(BSF_PHRASES)}")

@bot.command(name="عيلة")
async def family(ctx):
    await ctx.send("👑 العيلة: عجيب + أخوه الزعيم المؤسس ابو عيسى + موسى + موشي + معدن + اندي معدن = BSF للأبد 🔥")

@bot.command(name="اسال_موسى")
async def ask_musa(ctx, *, سؤال=""):
    if not سؤال:
        return await ctx.send("اكتب سؤال يا زلمة! مثال: `::اسال_موسى مين هو معدن؟`")
    async with ctx.typing():
        جواب = await ask_ai_for_musa(سؤال)
    embed = discord.Embed(title="🧠 موسى برد:", description=جواب, color=0x00FF00)
    embed.set_footer(text=f"سأل: {ctx.author.name} | {random.choice(BSF_PHRASES)}")
    await ctx.send(embed=embed)

bot.run(os.getenv("TOKEN"))
