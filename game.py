import discord
from discord.ext import commands
from discord import app_commands
import json, os, random

DATA_FILE = "bsf_data.json"

# --- خريطة عالم الدود ---
ROOMS = [
    {"name": "🌀 مغسلة الغسالات", "desc": "ريحة صابون ودودة عالقة بالجرابات!", "emoji": "🌀"},
    {"name": "🧦 جبل الجرابات الضايعة", "desc": "كل فردة بتدور على اختها، والدود مسيطر!", "emoji": "🧦"},
    {"name": "🍕 مطبخ بيتزا منتهية", "desc": "الببروني بتحرك لحاله... هاي دودة متنكرة!", "emoji": "🍕"},
    {"name": "🕳️ حفرة البلوعة", "desc": "ظلام وصرصرة، بس في كنز دودي!", "emoji": "🕳️"},
    {"name": "👑 عرش ملك الدود", "desc": "وصلت للنهاية! هون بنام الملك العظيم", "emoji": "👑"},
]

WORM_EVENTS = [
    ("😱 لقيت دودة بترقص دبكة!", "+1 🐛"),
    ("🤢 شفت دودة بتسبح في الشاي!", "-1 ❤️ بس +1 🐛 شجاعة"),
    ("📜 ورقة قديمة: 'من يملك الدود يملك القوة'", "لا شي، بس حكمة"),
    ("💥 دودة انفجرت بوجهك! صار معك دود مضاعف!", "+2 🐛"),
    ("😴 الدودة نايمة، لا تصحيها", "رجعت لورا غرفة"),
]

def load_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(uid, data):
    uid = str(uid)
    if uid not in data:
        data[uid] = {"hearts": 5, "worms": 0, "worm_room": 0, "name": "مجهول"}
    return data[uid]

class WormView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=120)
        self.cog = cog
        self.user_id = user_id

    @discord.ui.button(label="🔍 استكشاف", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user_id:
            return await interaction.response.send_message("❌ مش مغامرتك انت!", ephemeral=True)

        data = load_data()
        u = get_user(self.user_id, data)

        # 25% حدث عشوائي
        if random.random() < 0.25:
            ev_text, ev_eff = random.choice(WORM_EVENTS)
            if "+2" in ev_eff: u["worms"] += 2
            elif "+1" in ev_eff: u["worms"] += 1
            if "رجعت" in ev_text:
                u["worm_room"] = max(0, u["worm_room"]-1)
            embed = discord.Embed(title="💫 حدث دودي عشوائي!", description=f"{ev_text}\n`{ev_eff}`", color=0xffd700)
        else:
            # تقدم طبيعي
            if u["worm_room"] < len(ROOMS)-1:
                u["worm_room"] += 1
                u["worms"] +=
