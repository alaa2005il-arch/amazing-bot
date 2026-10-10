import discord
from discord.ext import commands
import os
import random
from flask import Flask
from threading import Thread

# ==================== 1- موقع وهمي عشان Render ما يطفي ====================
app = Flask('')
@app.route('/')
def home():
    return "👑 BSF Bot is Live - الزعيم المؤسس ابو عيسى أخو عجيب"
def run(): app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run, daemon=True).start()
# ========================================================================

# ==================== 2- إعدادات البوت ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents, help_command=None)

BSF_PHRASES = [
    "👑 الزعيم المؤسس ابو عيسى أخو عجيب",
    "😴 معدن بضل أخوي حتى واحنا نايمين",
    "🔄 اندي معدن = موسى لما ينسى",
    "🤝 كلنا BSF إخوة للأبد"
]

COLOR = 0x9B59B6 # لون BSF البنفسجي الحلو

# ==================== 3- ذكاء موسى ====================
async def ask_musa_ai(q):
    try:
        import openai
        key = os.getenv("OPENAI_API_KEY")
        if not key: raise Exception()
        client = openai.AsyncOpenAI(api_key=key)
        sys = "انت موسى من BSF، جاوب بلهجة فلسطينية شبابية قصيرة ومضحكة مع ايموجي. العيلة: الزعيم ابو عيسى، عجيب، موسى، موشي، معدن، اندي معدن."
        r = await client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":sys},{"role":"user","content":q}])
        return r.choices[0].message.content
    except:
        return random.choice([
            f"بخصوص '{q}'؟ روح اسأل الزعيم المؤسس ابو عيسى أخو عجيب 👑",
            f"'{q}'؟ معدن بضل أخوي حتى واحنا نايمين 😴"
        ])

# ==================== 4- الأحداث ====================
@bot.event
async def on_ready():
    print(f"✅ BSF Bot جاهز: {bot.user}")

# ==================== 5- الأوامر المرتبة ====================

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    e = discord.Embed(title="👑 قائمة أوامر BSF", color=COLOR, description="كل الأوامر تبدأ بـ `::`")
    e.add_field(name="🐝 ::بي", value="يتأكد البوت شغال", inline=True)
    e.add_field(name="👨‍👩‍👧‍👦 ::عيلة", value="يعرض عيلة BSF", inline=True)
    e.add_field(name="🧠 ::اسال_موسى [سؤال]", value="اسأل موسى الذكي", inline=True)
    e.add_field(name="😴 ::معدن", value="جملة معدن المشهورة", inline=True)
    e.add_field(name="🎁 ::اتفاجئ", value="مفاجأة عشوائية", inline=True)
    e.set_footer(text=random.choice(BSF_PHRASES))
    await ctx.send(embed=e)

@bot.command(name="بي")
async def bee(ctx):
    e = discord.Embed(title="🐝 بوت بي شغال!", description=random.choice(BSF_PHRASES), color=COLOR)
    await ctx.send(embed=e)

@bot.command(name="عيلة")
async def family(ctx):
    e = discord.Embed(title="👑 عيلة BSF", color=COLOR)
    e.description = "**الزعيم المؤسس:** ابو عيسى أخو عجيب\n**الأعضاء:** عجيب - موسى - موشي العبقري - معدن - اندي معدن\n\n🤝 **كلنا أصدقاء وإخوة للأبد**"
    await ctx.send(embed=e)

@bot.command(name="معدن")
async def madan(ctx):
    e = discord.Embed(description=f"## 😴 معدن بضل أخوي حتى واحنا نايمين\n\n{random.choice(BSF_PHRASES)}", color=COLOR)
    await ctx.send(embed=e)

@bot.command(name="اسال_موسى")
async def ask_musa(ctx, *, سؤال=""):
    if not سؤال: return await ctx.send("❓ اكتب سؤال: `::اسال_موسى مين عجيب؟`")
    async with ctx.typing():
        جواب = await ask_musa_ai(سؤال)
    e = discord.Embed(title="🧠 موسى برد:", description=جواب, color=COLOR)
    e.set_footer(text=f"سأل: {ctx.author.display_name}")
    await ctx.send(embed=e)

@bot.command(name="اتفاجئ")
async def surprise(ctx):
    s = random.choice([
        "💥 الزعيم المؤسس دخل الشات!", "🪱 الدودة رجعت من الحظيرة!",
        "😴 معدن صحي من النوم!", "👑 عجيب بقول وين الدودة؟", "🤖 موشي صلح البوت!"
    ])
    e = discord.Embed(title="🎁 مفاجأة BSF", description=f"## {s}", color=random.randint(0, 0xFFFFFF))
    await ctx.send(embed=e)

bot.run(os.getenv("TOKEN"))
