import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

DATA_FILE = "bsf_data.json"

# --- خريطة عالم الدود - بهارات موشي ---
ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "مكان رطب ومظلم، ريحة تراب. هون بتتعلم الزحف.", "chance": 0.9, "img": "https://i.imgur.com/8QJ4sQb.png"},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "صوت غسالات بتلف، دود صغير مخبي جوات الجرابات!", "chance": 0.75, "img": "https://i.imgur.com/3Z7rQYd.png"},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا معكرونة وبشاميل، وليمة للدود الجوعان.", "chance": 0.6, "img": "https://i.imgur.com/L3a1n1x.png"},
    {"id": 3, "name": "سرداب الأسرار", "emoji": "📦", "desc": "كراكيب قديمة، هون BSF خبت اللور المقدس.", "chance": 0.45, "img": "https://i.imgur.com/K4x2y8m.png"},
    {"id": 4, "name": "سطح القمر", "emoji": "🌙", "desc": "الزعيم الأخير! برد وهدوء، بس دودة القمر الأسطورية هون.", "chance": 0.25, "img": "https://i.imgur.com/m9p0r4W.png"},
]

LORE = [
    "📜 اللور: BSF مش مجرد دود، هي فلسفة حياة - الزحف ببطء بس بثبات.",
    "📜 اللور: يقال أن أول دودة هربت من مغسلة الغسالات سنة 2005.",
    "📜 اللور: من يجمع 100 دودة يفتح بوابة سطح القمر.",
    "📜 اللور: الدودة السوداء لا تظهر الا للي قلبه مليان 🖤",
    "📜 اللور: علاء هو الأب الروحي لكل الدود."
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
        data[uid] = {"hearts": 0, "worms": 0, "room": 0, "last_daily": None, "name": "مجهول"}
        save_data(data)
    return data[uid], data

class WormView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="استكشاف 🔍", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user_id:
            await interaction.response.send_message("مش لعبتك هاي يا غالي!", ephemeral=True)
            return

        user, all_data = get_user(interaction.user.id)
        room = ROOMS[user["room"]]

        # نسبة الفوز حسب الغرفة
        roll = random.random()
        found = roll < room["chance"]

        emb = discord.Embed()
        if found:
            # أحداث عشوائية 20%
            event_roll = random.random()
            if event_roll < 0.1: # دودة ذهبية
                user["worms"] += 3
                emb.title = f"✨ دودة ذهبية في {room['name']}!"
                emb.description = "يا مجنون! لقيت 3 دود مرة وحدة! 🐛🐛🐛"
                emb.color = discord.Color.gold()
            elif event_roll < 0.2: # سم
                user["worms"] = max(0, user["worms"]-1)
                emb.title = f"☠️ دودة مسممة!"
                emb.description = "أكلت دودة فاسدة ورجعت دودة لورا... -1"
                emb.color = discord.Color.red()
            elif event_roll < 0.35:
                emb.title = random.choice(LORE)
                emb.description = f"استكشفت {room['emoji']} {room['name']} ولقيت لور + دودة!"
                emb.color = discord.Color.purple()
                user["worms"] += 1
            else:
                user["worms"] += 1
                emb.title = f"لقيت دودة في {room['name']} {room['emoji']}"
                emb.description = f"الدودة كانت مستخبية تحت {random.choice(['جراب','صحن معكرونة','كرتونة قديمة','الغسالة'])}"
                emb.color = discord.Color.green()

            # تقدم تلقائي
            if user["worms"] >= 5 and user["room"] == 0:
                user["room"] = 1
                emb.add_field(name="🔓 فتحت منطقة
