import discord
from discord.ext import commands
import os, json, random, requests
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return "👑 BSF Live - ابو عيسى 28 دودة 🪱"
def run(): app.run(host='0.0.0.0', port=int(os.getenv("PORT", 10000)))
Thread(target=run, daemon=True).start()

URL = os.getenv("UPSTASH_REDIS_REST_URL","").strip('"\'')
TOK = os.getenv("UPSTASH_REDIS_REST_TOKEN","").strip('"\'')
def upstash(*args):
    if not URL or not TOK: return None
    try:
        r = requests.post(URL, headers={"Authorization": f"Bearer {TOK}"}, json=list(args), timeout=10)
        return r.json().get("result")
    except: return None
def load():
    res = upstash("GET", "bsf_data")
    if res:
        try: return json.loads(res)
        except: pass
    return {}
def save(d):
    try: upstash("SET", "bsf_data", json.dumps(d, ensure_ascii=False))
    except: pass

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ جاهز: {bot.user}")
    try: await bot.tree.sync()
    except: pass

@bot.command(name="بي")
async def bee(ctx): await ctx.send("🐝 شغال! 28 دودة 👑")

@bot.hybrid_command(name="دود", description="احفر دود")
async def dod(ctx):
    await ctx.defer()
    data=load()
    uid=str(ctx.author.id)
    if uid not in data: data[uid]={"worms":0,"name":ctx.author.display_name}
    data[uid]["name"]=ctx.author.display_name
    data[uid]["worms"]+=random.randint(1,3)
    save(data)
    await ctx.send(f"🪱 مجموعك {data[uid]['worms']}")

bot.run(os.getenv("TOKEN"))
