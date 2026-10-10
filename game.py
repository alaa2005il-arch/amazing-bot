import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

DATA_FILE = "bsf_data.json"

ROOMS = [
    {"name": "Fungal Grotto 🍄", "desc": "البداية - كهف الفطر المضيء"},
    {"name": "Mossy Burrow 🌿", "desc": "جحر الطحالب الرطب"},
    {"name": "Crystal Cavern 💎", "desc": "كهف الكريستال بالنص"},
    {"name": "Egg Chamber 🥚", "desc": "غرفة بيض الدودة الأم"},
    {"name": "Treasure Nook 👑", "desc": "النهاية - كنز الدود!"},
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

PHRASES = [
    "BSF زعامة للأبد 🔥",
    "عجيب وابو عيسى الزعماء الحقيقيين 👑",
    "جمعت قلب جديد! ❤️",
]

# --- View للأزرار تبع لعبة الدودة ---
class WormView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="استكشاف ⬆️", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)
        
        # تأكد من وجود اللاعب
        if user_id not in data:
            data[user_id] = {"hearts": 0, "name": interaction.user.name, "worm_room": 0, "worms": 0}
        if "worm_room" not in data[user_id]:
            data[user_id]["worm_room"] = 0
            data[user_id]["worms"] = 0

        room_idx = data[user_id]["worm_room"]
        
        # حدث عشوائي 20%
        msg = ""
        if random.random() < 0.2:
            event = random.choice(["double", "poison", "lore"])
            if event == "double":
                data[user_id]["worms"] += 2
                msg = "\n✨ لقيت دودتين 🐛🐛 بدل وحدة!"
            elif event == "poison":
                data[user_id]["worm_room"] = max(0, room_idx - 1)
                msg = "\n🍄 فطر سام! رجعت غرفة لورا!"
                save_data(data)
            elif event == "lore":
                msg = "\n📜 رسالة من الدودة الأم: 'الكنز قريب...'"
        else:
            # حركة عادية
            if room_idx < 4:
                data[user_id]["worm_room"] += 1
                data[user_id]["worms"] += 1

        save_data(data)
        new_room_idx = data[user_id]["worm_room"]
        room = ROOMS[new_room_idx]

        # اذا فاز
        if new_room_idx == 4:
            embed = discord.Embed(
                title="🏆 فزت! وصلت الكنز 👑",
                description=f"{interaction.user.mention} ختمت خريطة الدودة!\nجمعت **{data[user_id]['worms']}** دودة 🐛{msg}",
                color=discord.Color.gold()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        embed = discord.Embed(
            title=f"{room['name']}",
            description=f"{room['desc']}\n\nدوداتك
