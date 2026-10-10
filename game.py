import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

DATA_FILE = "bsf_data.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- عالم الدود ---
ROOMS = [
    {"name": "Fungal Grotto 🍄", "desc": "كهف الفطر المضيء - البداية", "color": 0x8B4513},
    {"name": "Mossy Burrow 🌿", "desc": "جحر الطحالب الرطب والزحليطة", "color": 0x228B22},
    {"name": "Crystal Cavern 💎", "desc": "كهف الكريستال - نص الطريق!", "color": 0x00CED1},
    {"name": "Egg Chamber 🥚", "desc": "غرفة بيض الدودة الأم... خطر!", "color": 0xFFD700},
    {"name": "Treasure Nook 👑", "desc": "كنز الدود الأسطوري! انت فزت!", "color": 0xFF1493},
]

PHRASES = [
    "BSF زعامة للأبد 🔥",
    "عجيب وابو عيسى الزعماء الحقيقيين 👑",
    "جمعت قلب جديد! ❤️",
    "الدودة بتتطلع عليك... 🐛",
]

class WormView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    def get_embed(self):
        data = load_data()
        u = data.get(str(self.user_id), {})
        room_idx = u.get("worm_room", 0)
        room_idx = min(room_idx, len(ROOMS)-1)
        room = ROOMS[room_idx]

        embed = discord.Embed(
            title=f"🐛 {room['name']} [{room_idx+1}/{len(ROOMS)}]",
            description=f"{room['desc']}\n\n**دوداتك:** {u.get('worms',0)} 🐛\n**قلوبك:** {u.get('hearts',0)} ❤️",
            color=room['color']
        )
        embed.set_footer(text=f"مغامرة الدودة - BSF | يحرسها عجيب وابو عيسى")
        # هون بتحط صورك بعدين: embed.set_image(url="...")
        return embed

    @discord.ui.button(label="استكشاف ⬆️", style=discord.ButtonStyle.green, emoji="🐛")
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user_id:
            await interaction.response.send_message("مش مغامرتك! اكتب /لعبة لتبدأ انت.", ephemeral=True)
            return

        data = load_data()
        uid = str(self.user_id)
        if uid not in data: data[uid] = {"hearts":0, "worm_room":0, "worms":0, "name": interaction.user.name}
        if "worm_room" not in data[uid]: data[uid]["worm_room"]=0
        if "worms" not in data[uid]: data[uid]["worms"]=0

        # حدث عشوائي 20%
        if random.random() < 0.2:
            event = random.choice(["double", "poison", "lore"])
            if event == "double":
                data[uid]["worms"] += 2
                msg = "💥 لقيت عش دود! **+2 دودة!**"
            elif event == "poison":
                data[uid]["worm_room"] = max(0, data[uid]["worm_room"]-1)
                msg = "🍄 أكلت فطر سام! رجعت غرفة لورا 😵‍💫"
            else:
                msg = "👁️ همس الأم: `الكنز مش ذهب... الكنز هو الرحلة`"
        else:
            data[uid]["worms"] += 1
            data[uid]["worm_room"] += 1
            msg = f"🐛 زحفت للأمام! +1 دودة"

        save_data(data)

        # فوز؟
        if data[uid]["worm_room"] >= len(ROOMS)-1:
            data[uid]["worm_room"] = len(ROOMS)-1
            save_data(data)
            embed = self.get_embed()
            embed.title = "🏆 وصلت للكنز! 👑"
            embed.description = f"**{msg}**\n\n{embed.description}\n\n**مبروك! ختمت الخريطة! اكتب /لعبة عشان تعيد من الأول**"
            data[uid]["worm_room"] =
