import discord
from discord.ext import commands
from discord import app_commands
import json, os, random

DATA_FILE = "bsf_data.json"

# --- عالم الدود ---
ROOMS = [
    {"name": "🌀 مغسلة الغسالات", "desc": "ريحة صابون وغسالات بتلف، الدود هون صغير وبيستخبى جوا الجرابات", "emoji": "🧦"},
    {"name": "🍕 مطبخ الليل", "desc": "بقايا بيتزا وفتات خبز، الدود الملكي بيعشق هالمكان", "emoji": "🐛"},
    {"name": "📚 مكتبة الغبار", "desc": "كتب قديمة وغبرة، فيه دودة حكيمة بتحكي قصص BSF", "emoji": "📖"},
    {"name": "🔥 مصنع الأسرار", "desc": "ماكينات سخنة وصوت عالي، بدك قلب شجاع عشان تدخل", "emoji": "⚙️"},
    {"name": "👑 عرش الدود", "desc": "النهاية! هون ملك الدود بستناك، بس لازم تجمع 10 دودات", "emoji": "👑"},
]

PHRASES = [
    "BSF بتسأل: وين رحت مبارح؟",
    "القلب هرب من الخوف!",
    "دودة قالتلك: بدك بوسة ولا قلب؟",
    "لقيت قلب واقع على الأرض 💔",
    "BSF غارت منك!",
    "الدود بضحك عليك 😂",
]

LORE = [
    "أسطورة بتقول: اللي بجمع 10 دودات بصير ملك اللعاب!",
    "دودة حكيمة همست: لا تثق في الغسالة رقم 3",
    "لقيت ورقة مكتوب عليها: BSF كانت هون...",
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

def get_user(uid, data):
    uid = str(uid)
    if uid not in data:
        data[uid] = {"hearts": 0, "worms": 0, "worm_room": 0, "name": "مجهول"}
    # تأكد من الحقول القديمة
    data[uid].setdefault("hearts", 0)
    data[uid].setdefault("worms", 0)
    data[uid].setdefault("worm_room", 0)
    return data[uid]

# --- View بالأزرار ---
class WormView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=180)
        self.cog = cog
        self.user_id = user_id

    async def make_embed(self, uid):
        data = load_data()
        u = get_user(uid, data)
        room = ROOMS[u["worm_room"] % len(ROOMS)]
        embed = discord.Embed(
            title=f"{room['emoji']} {room['name']}",
            description=f"{room['desc']}\n\n**غرفة:** {u['worm_room']+1}/{len(ROOMS)}\n**دوداتك:** {u['worms']}🐛 | **قلوبك:** {u['hearts']}❤️",
            color=0x8B5CF6
        )
        embed.set_footer(text=f"اللاعب: {u['name']} | استكشف عشان تلاقي دود")
        return embed

    @discord.ui.button(label="🔍 استكشاف", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id!= self.user_id:
            return await interaction.response.send_message("هاي مش مغامرتك! اكتب /لعبة", ephemeral=True)

        data = load_data()
        u = get_user(self.user_id, data)
        roll = random.random()

        msg = ""
        if roll < 0.20: # حدث نادر
            event = random.choice(["double", "poison", "lore"])
            if event == "double":
                u["worms"] += 2
                msg = "🔥 **حدث نادر!** لقيت دودتين توأم! +2🐛"
            elif event == "poison":
                u["worm_room"] = max(0, u["worm_room"]-1)
                msg = "☠️ دودة مسمومة! رجعتك غرفة لورا!"
            else:
                msg = f"📜 **سر:** {random.choice(LORE)}"
        elif roll < 0.65: # لقى دودة
            u["worms"] += 1
            u["worm_room"] += 1
            msg = f"🐛 مسكت دودة! +1 | {random.choice(PHRASES)}"
            # كل 3 دودات = قلب
            if u["worms"] % 3 == 0:
                u["hearts"] += 1
                msg += "\n❤️ 3 دودات = قلب جديد!"
        else:
            msg = f"💨 ما لقيت شي... {random.choice(PHRASES)}"

        # فوز؟
        if u["worm_room"] >= len(ROOMS):
            u["worm_room"] = len(ROOMS)-1
            if u["worms"] >= 10:
                msg += "\n\n👑 **مبروووك! صرت ملك اللعاب!** 👑"

        u["name"] = interaction.user.display_name
        save_data(data
