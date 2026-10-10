import os
import json
import random
import io
import datetime
import traceback
import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from flask import Flask
from threading import Thread

DATA_FILE = "bsf_data.json"

# ===== Keep Alive - عشان ما يطفي على Render =====
app = Flask('')
@app.route('/')
def home():
    return "BSF-BOT Online ♾️🪱"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()
    print("✅ Flask Keep Alive شغال")

# ===== غرف الدود =====
WORM_ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "مكان رطب ومظلم", "chance": 0.85, "worms": 1, "color": 0x8B4513},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "الدود مخبي جوا الجرابات", "chance": 0.70, "worms": 2, "color": 0x00BFFF},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا أكل، جنة الدود", "chance": 0.60, "worms": 3, "color": 0xFFA500},
    {"id": 3, "name": "سرداب الاسرار", "emoji": "📦", "desc": "كراكيب BSF القديمة", "chance": 0.45, "worms": 5, "color": 0x800080},
    {"id": 4, "name": "ثلاجة الموتى", "emoji": "🧊", "desc": "دود نادر وغالي", "chance": 0.30, "worms": 8, "color": 0xADD8E6},
    {"id": 5, "name": "عرش BSF الذهبي", "emoji": "👑", "desc": "دودة ذهبية ♾️", "chance": 0.15, "worms": 15, "color": 0xFFD700},
]

WORM_TYPES = [
    {"name": "دودة عادية", "emoji": "🪱", "value": 1},
    {"name": "دودة مشعة", "emoji": "✨", "value": 3},
    {"name": "دودة ذهبية", "emoji": "👑", "value": 10},
]

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_data(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Save Error: {e}")

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"worms": 0, "gold": 0, "level": 1, "xp": 0, "inventory": [], "last_hunt": None}
        save_data(data)
    return data[uid], data

# ===== البوت =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} - BSF شغال ♾️')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e: print(e)

# هذا اهم اشي - عشان لو امر خرب ما يطفي البوت
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"ERROR in /{interaction.command.name}: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ صار ايرور: {error}\nبس البوت ما طفي ♾️", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ صار ايرور: {error}", ephemeral=True)
    except: pass

@bot.hybrid_command(name="دود", description="احفر ودور دود")
@app_commands.choices(غرفة=[app_commands.Choice(name=f"{r['emoji']} {r['name']}", value=r['id']) for r in WORM_ROOMS])
async def worm_hunt(ctx, غرفة: int = 0):
    try:
        await ctx.defer() #
