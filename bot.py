import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

# --- تخزين البيانات ---
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

# --- خريطة الدودة BSF WORM WORLD MAP ---
ROOMS = [
    {"id": 0, "name": "Fungal Grotto 🍄", "desc": "البداية - كهف الفطر المضيء، هون بتبلش رحلة الزعامة", "emoji": "🍄"},
    {"id": 1, "name": "Mossy Burrow 🌿", "desc": "جحر الطحالب الرطب، ريحة تراب ودود صغير", "emoji": "🌿"},
    {"id": 2, "name": "Crystal Cavern 💎", "desc": "كهف الكريستال - النص، الكريستال بيلمع والطريق بخوف", "emoji": "💎"},
    {"id": 3, "name": "Egg Chamber 🥚", "desc": "غرفة بيض الدودة الأم، لا تصحيها!", "emoji": "🥚"},
    {"id": 4, "name": "Treasure Nook 👑", "desc": "النهاية - كنز BSF! تاج الزعامة بستناك", "emoji": "👑"},
]

PHRASES = [
    "BSF زعامة للأبد 🔥",
    "عجيب وابو عيسى الزعماء الحقيقيين 👑",
    "جمعت قلب جديد! ❤️",
    "اهرب من الغسالة! 🌀",
]

RANDOM_EVENTS = [
    {"type": "double", "msg": "يا وحش! لقيت دودتين 🐛🐛 بدل وحدة!", "worms": 2},
    {"type": "poison", "msg": "أووبس! أكلت فطر سام 🍄 رجعتك غرفة لورا!", "worms": 0, "back": True},
    {"type": "lore", "msg": "📜 رسالة غامضة من الدودة الأم: 'الزعيم الحقيقي لا يخاف الظلام...'", "worms": 1},
]

# --- View بالأزرار لمغامرة الدودة ---
class WormView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300) # 5 دقايق

    def get_embed(self, user: discord.Member, user_data: dict):
        room_id = user_data.get("worm_room", 0)
        worms = user_data.get("worms", 0)
        room = ROOMS[room_id]

        progress = "—" * 5
        progress_list = list(progress)
        for i in range(room_id + 1):
            progress_list[i] = "●"
        progress_bar = "".join(progress_list)

        embed = discord.Embed(
            title=f"{room['emoji']} {room['name']}",
            description=f"{room['desc']}\n\n`{progress_bar}` {room_id+1}/5",
            color=discord.Color.green() if room_id < 4 else discord.Color.gold()
        )
        embed.add_field(name="🐛 دوداتك", value=f"**{worms}** دودة", inline=True)
        embed.add_field(name="📍 الموقع", value=room['name'], inline=True)
        embed.set_author(name=f"مغامرة {user.display_name}", icon_url=user.display_avatar.url)
        embed.set_footer(text="BSF WORM WORLD MAP - اضغط استكشاف للمتابعة")
        # لما تبعتلي الصور، بتحط هون: embed.set_image(url=...)
        return embed

    @discord.ui.button(label="استكشاف ⬆️", style=discord.ButtonStyle.green, emoji="🐛")
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)

        if user_id not in data:
            data[user_id] = {"hearts": 0, "name": interaction.user.name, "worm_room": 0, "worms": 0}

        # تأكد من وجود حقول الدودة
        data[user_id].setdefault("worm_room", 0)
        data[user_id].setdefault("worms", 0)

        room_id = data[user_id]["worm_room"]

        # اذا فايز من قبل و
