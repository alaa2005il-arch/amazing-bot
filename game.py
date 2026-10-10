import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import json
import os

DATA_FILE = "bsf_data.json"

ROOMS = [
    {"id": 0, "name": "Fungal Grotto 🍄", "desc": "البداية - رائحة الفطر في كل مكان", "emoji": "🍄"},
    {"id": 1, "name": "Mossy Burrow 🌿", "desc": "جحر الطحالب - طريق زلق وآمن", "emoji": "🌿"},
    {"id": 2, "name": "Crystal Cavern 💎", "desc": "كهف الكريستال - النص، الدودات بتلمع هون", "emoji": "💎"},
    {"id": 3, "name": "Egg Chamber 🥚", "desc": "غرفة البيض - الدودة الأم بتحرس", "emoji": "🥚"},
    {"id": 4, "name": "Treasure Nook 👑", "desc": "كنز الزعامة! وصلت للنهاية", "emoji": "👑"},
]

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

def get_user(data, user_id, name):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"hearts": 0, "name": name, "worm_room": 0, "worms": 0}
    # لضمان التوافق مع البيانات القديمة
    data[uid].setdefault("worm_room", 0)
    data[uid].setdefault("worms", 0)
    data[uid].setdefault("hearts", 0)
    data[uid]["name"] = name
    return data[uid]

PHRASES = [
    "BSF زعامة للأبد 🔥",
    "عجيب وابو عيسى الزعماء الحقيقيين 👑",
    "الدودة جمعت قوة جديدة! 🐛",
]

LORE = [
    "سمعت همس الدودة الأم: 'استمر يا صغيري...'",
    "فطر غريب اضاء طريقك فجأة ✨",
    "أثر دودة قديمة... كانت هنا قبلك",
]

class WormView(View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="استكشاف ⬆️", style=discord.ButtonStyle.green, emoji="🐛")
    async def explore(self, interaction: discord.Interaction, button: Button):
        data = load_data()
        user = get_user(data, interaction.user.id, interaction.user.name)

        # حدث عشوائي 20%
        event_text = ""
        if random.random() < 0.2:
            event = random.choice(["double", "back", "lore"])
            if event == "double":
                user["worms"] += 2
                user["worm_room"] = min(4, user["worm_room"] + 1)
                event_text = "\n✨ **حدث نادر!** لقيت دودتين مرة وحدة! ❤️❤️"
            elif event == "back":
                user["worm_room"] = max(0, user["worm_room"] - 1)
                event_text = "\n🍄 **فطر سام!** رجعتك خطوة لورا!"
            else:
                event_text = f"\n📜 {random.choice(LORE)}"
        else:
            user["worms"] += 1
            user["worm_room"] = min(4, user["worm_room"] + 1)

        save_data(data)
        room = ROOMS[user["worm_room"]]

        if room["id"] == 4:
            embed = discord.Embed(
                title=f"{room['name']} - فزت!",
                description=f"{interaction.user.mention} وصل لكنز الزعامة! 👑\n\nجمعت **{user['worms']}** دودة في الرحلة!\n{event_text}\n\nاكتب `/زعامة` لتشوف الترتيب",
                color=discord.Color.gold()
            )
            embed.set_footer(text="BSF Worm World - النهاية")
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title=f"{room['emoji']} {room['name']}",
                description=f"{room['desc']}\n\n**الدودات:** 🐛 {user['worms']}\n**
