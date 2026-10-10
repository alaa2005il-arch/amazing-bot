import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

DATA_FILE = "bsf_data.json"

# --- عالم الدود ---
ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "حفرة رطبة ومظلمة، بداية كل دودة اسطورية"},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "صوت غسالات، وجرابات ضايعة مليانة دود"},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "ريحة معكرونة بايتة، الدود هون شبعان"},
    {"id": 3, "name": "سرداب الأسرار", "emoji": "📦", "desc": "كراتين قديمة وفيها لور BSF السري"},
    {"id": 4, "name": "سطح القمر", "emoji": "🌙", "desc": "مكان الزعيم، بس اللي معه 10 دودات بدخل"},
]

LORE_TEXTS = [
    "📜 لور: أول دودة BSF هربت من المختبر سنة 2003",
    "📜 لور: الغسالة رقم 3 بتبلع جرابات عشان تطعمي الدود",
    "📜 لور: اللي يجمع 50 قلب بتحول لـ Worm King",
    "📜 لور: سطح القمر مش قمر حقيقي، هو لمبة الحمام",
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

def get_user(data, uid, name):
    uid = str(uid)
    if uid not in data:
        data[uid] = {"name": name, "hearts": 0, "worms": 0, "worm_room": 0, "last_daily": ""}
    else:
        data[uid]["name"] = name
        if "worms" not in data[uid]: data[uid]["worms"] = 0
        if "worm_room" not in data[uid]: data[uid]["worm_room"] = 0
        if "hearts" not in data[uid]: data[uid]["hearts"] = 0
    return data[uid]

class WormView(discord.ui.View):
    def __init__(self, cog, user_id):
