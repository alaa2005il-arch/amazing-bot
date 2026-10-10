import discord
from discord.ext import commands
from discord import app_commands
import json, os, random, asyncio
from datetime import datetime

DATA_FILE = "bsf_data.json"

# --- عالم الدود ---
ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "ريحة رطوبة وتراب، اول مكان بيصحى فيه الدود", "chance": 0.85},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "صوت مي وغسالات، الدود بتخبى جوا الجرابات", "chance": 0.70},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا معكرونة وزيت، وليمة للدود الجوعان", "chance": 0.60},
    {"id": 3, "name": "سرداب الأسرار", "emoji": "📦", "desc": "كراكيب قديمة وصندوق BSF الأسود، في لور مخفي هون", "chance": 0.45},
    {"id": 4, "name": "سطح القمر - عرش الملك", "emoji": "🌙", "desc": "بس ملوك الدود بوصلوا هون، فرصة قليلة بس الجائزة اسطورية", "chance": 0.25},
]

LORE = [
    "📜 لور: اول دودة في BSF انخلقت من جراب ضايع بالغسالة سنة 2023",
    "📜 لور: موشي هو الوحيد اللي شاف ملكة الدود ونفد",
    "📜 لور: في دودة ذهبية بتظهر مرة كل 100 استكشاف",
    "📜 لور: اللي بيوصل لسطح القمر بصير ملك الدود رسمياً",
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"hearts": 0, "worms": 0, "room": 0, "explores": 0, "lore": []}
    return data, data[uid]

class WormView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="استكشف 🔍", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user_id:
            return await interaction.response.send_message("مش لعبتك يا حب 😏", ephemeral=True)

        data, user = get_user(interaction.user.id
