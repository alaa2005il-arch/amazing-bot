import os, json, random, traceback, discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import requests

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").strip().strip('"').strip("'")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip().strip('"').strip("'")

def upstash_command(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN: return None
    try:
        r = requests.post(UPSTASH_URL, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, json=list(args), timeout=10)
        return r.json().get("result")
    except: return None

DATA_FILE = "bsf_data.json"
def load_data():
    res = upstash_command("GET", "bsf_data")
    if res:
        try: return json.loads(res)
        except: pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return {}
def save_data(data):
    try: upstash_command("SET", "bsf_data", json.dumps(data, ensure_ascii=False))
    except: pass
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass
def get_user(uid):
    data = load_data(); uid = str(uid)
    if uid not in data:
        data[uid] = {"worms":0,"gold":0,"level":1,"xp":0,"inventory":[],"name":str(uid)}
        save_data(data)
    return data[uid], data

# ==== رتب ابو عيسى VIP ====
VIP_USERS = {
    # تقدر تضيف ايدي الديسكورد هون - هلا شغال على الاسم
    "ابو عيسى": {"title": "👑 المؤسس", "color": 0xFF0000},
    "عيسى": {"title": "👑 المؤسس", "color": 0xFF0000},
    "موشي": {"title": "⚙️ المطور", "color": 0x00FF00},
    "موسى": {"title": "⚙️ المطور", "color": 0x00FF00},
    "عجيب": {"title": "🔥 عجيب BSF", "color": 0xFFD700},
}

def get_vip_info(display_name):
    name_lower = display_name.lower()
    for key, info in VIP_USERS.items():
        if key.lower() in name_lower:
            return info
    return None

app = Flask('')
@app.route('/')
def home(): return "BSF BOT Online ♾️ VIP ابو عيسى"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): Thread(target=run_flask, daemon=True).start()

WORM_ROOMS = [
    {"id":0,"name":"حفرة البداية","emoji":"🕳️","desc":"مكان رطب ومظلم","chance":0.85,"worms":1,"color":0x8B4513},
    {"id":1,"name":"مغسلة الغسالات","emoji":"🌀","desc":"الدود مخبي جوا الجرابات","chance":0.70,"worms":2,"color":0x00BFFF},
    {"id":2,"name":"مطبخ العمارة","emoji":"🍝","desc":"بقايا أكل، جنة الدود","chance":0.60,"worms":3,"color":0xFFA500},
    {"id":3,"name":"سرداب الاسرار","emoji":"📦","desc":"كراكيب BSF القديمة","chance":0.45,"worms":5,"color":0x800080},
    {"id":4,"name":"ثلاجة الموتى","emoji":"🧊","desc":"دود نادر وغالي","chance":0.30,"worms":8,"color":0xADD8E6},
    {"id":5,"name":"عرش BSF الذهبي","emoji":"👑","desc":"دودة ذهبية ♾️","chance":0.15,"worms":15,"color":0xFFD700},
]
WORM_TYPES = [
    {"name":"دودة عادية","emoji":"🪱","value":1},
    {"name":"دودة مشعة","emoji":"✨","value":3},
    {"name":"دودة ذهبية","emoji":"👑","value":10},
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} - BSF VIP READY ابو عيسى')
    try: await bot.tree.sync()
    except: pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"ERROR /{interaction.command.name}: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ صار ايرور بس البوت ما طفي ♾️", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ ايرور: {error}", ephemeral=True)
    except: pass

@bot.hybrid_command(name="دود", description="احفر ودور دود")
@app_commands.choices(غرفة=[app_commands.Choice(name=f"{r['emoji']} {r['name']}", value=r['id']) for r in WORM_ROOMS])
async def worm_hunt(ctx, غرفة: int = 0):
    await ctx.defer()
    room = WORM_ROOMS[غرفة] if 0 <= غرفة < len(WORM_ROOMS) else WORM_ROOMS[0]
    user_data, all_data = get_user(ctx.author.id)
    user_data["name"] = ctx.author.display_name
    vip = get_vip_info(ctx.author.display_name)

    if random.random() > room["chance"]:
        embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=f"{room['desc']}\n\n❌ **ما لقيت ولا دودة!**", color=room["color"])
        if vip: embed.set_author(name=f"{ctx.author.display_name} {vip['title']}")
        await ctx.send(embed=embed); save_data(all_data); return

    amount = random.randint(1, room["worms"])
    worm_type = random.choices(WORM_TYPES, weights=[70,20,10])[0]
    total = amount * worm_type["value"]
    # ابو عيسى باخد دبل ذهب 😎
    if vip and "المؤسس" in vip["title"]:
        total *= 2
        amount *= 2

    user_data["worms"] += total; user_data["xp"] += total*2; user_data["gold"] += total
    if user_data["xp"] >= user_data["level"]*100: user_data["level"] += 1
    save_data(all_data)

    color = vip["color"] if vip else room["color"]
    title_vip = f" {vip['title']}" if vip else ""
    embed = discord.Embed(title=f"{room['emoji']} {room['name']} - لقيت دود!{title_vip}", description=f"{room['desc']}\n\n{worm_type['emoji']} **{worm_type['name']}** x{amount}\n💰 +{total} ذهب{' (دبل للمؤسس 👑)' if vip and 'المؤسس' in vip['title'] else ''}\n🪱 مجموع الدود: {user_data['worms']}\n⭐ لفل: {user_data['level']} | XP: {user_data['xp']}", color=color)
    embed.set_footer(text=f"محفوظ في Upstash Frankfurt ♾️ | {ctx.author.display_name} {vip['title'] if vip else ''}")
    if vip: embed.set_author(name=f"{ctx.author.display_name} {vip['title']}")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="احصائيات", description="شوف احصائياتك")
async def stats(ctx):
    user_data,_ = get_user(ctx.author.id)
    vip = get_vip_info(ctx.author.display_name)
    color = vip["color"] if vip else 0xFFD700
    title = f"📊 احصائيات {ctx.author.display_name} {vip['title'] if vip else ''}"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="🪱 دود", value=str(user_data.get("worms",0)), inline=True)
    embed.add_field(name="💰 ذهب", value=str(user_data.get("gold",0)), inline=True)
    embed.add_field(name="⭐ لفل", value=str(user_data.get("level",1)), inline=True)
    embed.add_field(name="✨ XP", value=str(user_data.get("xp",0)), inline=True)
    if vip: embed.add_field(name="👑 الرتبة", value=vip["title"], inline=False)
    embed.set_footer(text="محفوظ للأبد في Upstash ♾️ | ابو عيسى VIP")
    if vip: embed.set_author(name=f"{ctx.author.display_name} {vip['title']}")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="توب", description="توب 10 اكثر ناس جمعو دود")
async def top_worms(ctx):
    await ctx.defer()
    data = load_data()
    if not data: await ctx.send("❌ لسه ما حدا جمع دود!"); return
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("worms",0), reverse=True)[:10]
    embed = discord.Embed(title="🏆 توب 10 صيادين الدود BSF 👑🪱", description="اكثر ناس جمعو دود", color=0xFFD700)
    medals=["🥇","🥈","🥉"]; text=""
    for i,(uid,udata) in enumerate(sorted_users):
        name=udata.get("name",f"User {uid[:4]}")
        worms=udata.get("worms",0); level=udata.get("level",1)
        vip = get_vip_info(name)
        vip_tag = f" {vip['title']}" if vip else ""
        medal=medals[i] if i<3 else f"**{i+1}**."; text+=f"{medal} **{name}**{vip_tag} - 🪱 {worms} | ⭐ لفل {level}\n"
    embed.add_field(name="الترتيب", value=text or "لا يوجد", inline=False)
    embed.set_footer(text=f"مجموع اللاعبين: {len(data)} | Upstash Frankfurt ♾️ | ابو عيسى 👑")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="ليدربورد", description="نفس التوب")
async def leaderboard(ctx): await top_worms(ctx)

@bot.hybrid_command(name="اوامر", description="كل اوامر لعبة BSF")
async def awamer(ctx):
    embed = discord.Embed(title="🔥【BSF】🔥 - دليل لعبة الدود الكامل 🪱♾️", description="""
**البوت مربوط على Upstash Frankfurt 🇩🇪 - كل شي محفوظ للأبد ♾️**

🎮 **/دود [الغرفة]** - احفر ودور دود
📊 **/احصائيات** - شوف دودك وذهبك ولفلك
🏆 **/توب** - توب 10 صيادين الدود
📜 **/اوامر** - هاد الدليل

🗺️ **الغرف:** 🕳️ 85% | 🌀 70% | 🍝 60% | 📦 45% | 🧊 30% | 👑 15%
✨ **الدود:** 🪱 1 ذهب | ✨ 3 ذهب | 👑 10 ذهب
⭐ كل دودة = 2 XP | كل 100 XP = لفل

👑 **ابو عيسى** - المؤسس - دبل ذهب ودود! ♾️
⚙️ **موشي & موسى** - المطورين
🔥 **عجيب** - BSF

صيد موفق يا بطل BSF! 🪱🔥
""", color=0xFFD700)
    embed.set_footer(text="BSF BOT | Upstash Frankfurt ♾️ | ابو عيسى المؤسس 👑")
    await ctx.send(embed=embed)

keep_alive()
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN") or os.getenv("BOT_TOKEN")
if TOKEN: bot.run(TOKEN)
