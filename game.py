import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

DATA_FILE = "bsf_data.json"

# ===== غرف الدود المكتملة =====
WORM_ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "مكان رطب ومظلم، تسمع صوت دود يزحف تحت رجليك", "chance": 0.85, "worms": 1, "color": 0x8B4513},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "ريحة مسحوق غسيل وصوت مية، الدود مخبي جوا الجرابات", "chance": 0.70, "worms": 2, "color": 0x00BFFF},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا أكل ومعكرونة، جنة الدود الجوعان", "chance": 0.60, "worms": 3, "color": 0xFFA500},
    {"id": 3, "name": "سرداب الاسرار", "emoji": "📦", "desc": "كراكيب BSF القديمة، هون اللور الحقيقي مدفون", "chance": 0.45, "worms": 5, "color": 0x800080},
    {"id": 4, "name": "ثلاجة الموتى", "emoji": "🧊", "desc": "برد قاتل، الدود هون نادر بس غالي كثير", "chance": 0.30, "worms": 8, "color": 0xADD8E6},
    {"id": 5, "name": "عرش BSF الذهبي", "emoji": "👑", "desc": "ممنوع الدخول الا للأساطير، دودة ذهبية ♾️", "chance": 0.15, "worms": 15, "color": 0xFFD700},
]

WORM_TYPES = [
    {"name": "دودة عادية", "emoji": "🪱", "value": 1},
    {"name": "دودة مشعة", "emoji": "✨", "value": 3},
    {"name": "دودة ذهبية", "emoji": "👑", "value": 10},
]

# ===== حفظ وتحميل =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"worms": 0, "gold": 0, "level": 1, "xp": 0, "inventory": [], "last_hunt": None}
        save_data(data)
    return data[uid]

# ===== اعداد البوت =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} - BSF WORM BOT شغال ♾️🪱')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash commands')
    except Exception as e:
        print(e)
    await bot.change_presence(activity=discord.Game(name="صيد الدود 🪱 |!دود"))

# ===== أمر الصيد =====
@bot.hybrid_command(name="دود", description="انزل تحفر وتدور دود في غرف BSF")
@app_commands.describe(غرفة="اختار وين بدك تحفر")
@app_commands.choices(غرفة=[
    app_commands.Choice(name=f"{r['emoji']} {r['name']}", value=r['id']) for r in WORM_ROOMS
])
async def worm_hunt(ctx, غرفة: int = 0):
    user_data = get_user(ctx.author.id)
    all_data = load_data()

    # كولداون 15 ثانية
    if user_data.get("last_hunt"):
        last = datetime.datetime.fromisoformat(user_data["last_hunt"])
        diff = (datetime.datetime.now() - last).total_seconds()
        if diff < 15:
            await ctx.send(f"⏳ اهدى يا {ctx.author.mention}، المجرفة حميت! استنى {int(15-diff)} ثانية", ephemeral=True)
            return

    room = WORM_ROOMS[غرفة]
    roll = random.random()

    embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=room['desc'], color=room['color'])
    embed.set_footer(text=f"BSF WORM HUNT | {ctx.author.display_name}")

    if roll <= room["chance"]:
        found_worm = random.choice(WORM_TYPES)
        # حظ الغرف النادرة يعطي دود اغلى
        if room["id"] >= 4 and random.random() < 0.5:
            found_worm = WORM_TYPES[2]
        elif room["id"] >= 2 and random.random() < 0.4:
            found_worm = WORM_TYPES[1]

        amount = random.randint(1, room["worms"])
        value = amount * found_worm["value"]

        user_data["worms"] += amount
        user_data["gold"] += value
        user_data["xp"] +=
