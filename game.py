import 【entity-discord¦canonical_name=discord】
from 【entity-discord¦canonical_name=discord】.ext import commands
from 【entity-discord¦canonical_name=discord】 import app_commands
import random
import json
import os

DATA_FILE = "bsf_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- عبارات BSF القديمة ---
PHRASES = [
    "BSF زعامة للأبد 🔥",
    "عجيب وابو عيسى الزعماء الحقيقيين 👑",
    "جمعت قلب جديد! ❤️",
    "اهرب من الغسالة! 🌀",
    "الثقب ظهر! مين بيلقطه أول؟ 🕳️"
]

# --- خريطة عالم الدود الجديدة ---
ROOMS = [
    {"id": 0, "name": "مغسلة الغسالات المكسورة", "emoji": "🌀", "desc": "ريحة صابون و صوت غسالة بتلف لحالها. هون بلشت الاسطورة.", "lore": "كاسر الغسالات كان هون قبل ما يختفي..."},
    {"id": 1, "name": "ثقب المجاري السري", "emoji": "🕳️", "desc": "ثقب ضيق و رطب. بتسمع صوت دود بيزحف.", "lore": "الدود بطلع من هون بالليل."},
    {"id": 2, "name": "مملكة قلوب BSF", "emoji": "❤️", "desc": "كل القلوب اللي جمعوها الشباب بتتخزن هون.", "lore": "عجيب وابو عيسى بنوا هاي المملكة قلب قلب."},
    {"id": 3, "name": "كهف كاسر الغسالات", "emoji": "🔨", "desc": "مليان قطع غسالات مكسرة و مفكات.", "lore": "اذا لقيت المفك الذهبي، بتصير زعيم."},
    {"id": 4, "name": "عرش الزعامة النهائي", "emoji": "👑", "desc": "بس اللي معه 10 دودات بوصل ه
