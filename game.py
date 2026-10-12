import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random

DATA_FILE = "bsf_data.json"

WORM_ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "مكان رطب ومظلم، تسمع صوت دود يزحف تحت رجليك", "chance": 0.85, "worms": 1},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "ريحة مسحوق غسيل وصوت مية، الدود مخبي جوا الجرابات", "chance": 0.70, "worms": 2},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا أكل ومعكرونة، جنة الدود الجوعان", "chance": 0.60, "worms": 3},
    {"id": 3, "name": "سرداب الاسرار", "emoji": "📦", "desc": "كراكيب BSF القديمة، هون اللور الحقيقي مدفون", "chance": 0.45, "worms": 5},
    {"id": 4, "name": "سطح القمر - عرش الدودة", "emoji": "🌙", "desc": "الزعيم الأخير، بس ملك اللعاب بقدر يوصلو", "chance": 0.25, "worms": 10},
]

BSF_LORE = [
    "لور: BSF تأسست من غسالة خربانة سنة 2021",
    "لور: موشي اكل 3 دودات مرة وحدة وفكرها معكرونة",
    "بهار: اضرب الدودة بالفلفل الاسود بتقوى!",
    "لور: زعيم الدود كان صديق الغسالة",
    "بهار: الدود بحب الكمون زيك يا موشي",
    "سر: في دودة ذهبية بتطلع بس الساعة 4:45 الفجر!",
]
PHRASES = ["قلبك مليان دود يا وحش!", "دودة ورا دودة والقلوب بتزيد", "يا موشي انت ملك اللعاب رسمي!", "بهارتك يا موشي!"]

# Redis support زي بهاراتك
try:
    import redis.asyncio as redis
    REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None
except:
    redis_client = None

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

async def load_user_async(uid):
    uid = str(uid)
    if redis_client:
        try:
            d = await redis_client.hgetall(f"user:{uid}")
            if d:
                return {
                    "hearts": int(d.get("hearts", 0)),
                    "worms": int(d.get("worms", 0)),
                    "worm_room": int(d.get("worm_room", 0)),
                    "explores": int(d.get("explores", 0)),
                    "last_daily": d.get("last_daily"),
                    "quiz_level": int(d.get("quiz_level", 0)),
                    "quiz_coins": int(d.get("quiz_coins", 0)),
                }
        except: pass
    # fallback
    all_data = load_data()
    if uid not in all_data:
        all_data[uid] = {"hearts":0,"worms":0,"worm_room":0,"explores":0,"last_daily":None,"quiz_level":0,"quiz_coins":0}
        save_data(all_data)
    return all_data.get(uid, {"hearts":0,"worms":0,"worm_room":0,"explores":0,"last_daily":None,"quiz_level":0,"quiz_coins":0})

async def save_user_async(uid, ud):
    uid = str(uid)
    if redis_client:
        try:
            await redis_client.hset(f"user:{uid}", mapping={k: str(v) for k,v in ud.items() if v is not None})
            return
        except: pass
    all_data = load_data()
    all_data[uid] = ud
    save_data(all_data)

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"hearts":0,"worms":0,"worm_room":0,"explores":0,"last_daily":None,"quiz_level":0,"quiz_coins":0}
        save_data(data)
    return data[uid]

class WormView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="استكشاف 🕳️", style=discord.ButtonStyle.green)
    async def explore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("مش لعبتك يا غالي!", ephemeral=True)
            return
        await interaction.response.defer()
        u = await load_user_async(self.user_id)
        room = WORM_ROOMS[min(u["worm_room"], len(WORM_ROOMS)-1)]
        u["explores"] += 1
        roll = random.random()
        if roll < room["chance"]:
            found = room["worms"] + random.randint(0,2)
            if random.random() < 0.15:
                found *= 2
                msg = f"**بهارتك يا موشي! 🔥** لقيت دودة مبهرة!\n+{found} دودات في {room['emoji']} {room['name']}"
            else:
                msg = f"لقيت {found} دودات في {room['emoji']} {room['name']}!\n{random.choice(PHRASES)}"
            u["worms"] += found
            u["hearts"] += found
            if u["explores"] % 5 == 0 and u["worm_room"] < len(WORM_ROOMS)-1:
                u["worm_room"] += 1
                msg += f"\n\n**فتحت منطقة جديدة!** ➡️ {WORM_ROOMS[u['worm_room']]['emoji']} {WORM_ROOMS[u['worm_room']]['name']}"
        else:
            if random.random() < 0.5:
                msg = f"ما لقيت اشي... بس لقيت ورقة:\n> {random.choice(BSF_LORE)}"
            else:
                msg = f"فش دود في {room['name']}... الدود هرب! {room['emoji']}"
        await save_user_async(self.user_id, u)
        embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=msg, color=0x8B4513)
        embed.add_field(name="دودك", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="قلوبك", value=f"{u['hearts']} ❤️", inline=True)
        embed.set_footer(text=f"استكشافات: {u['explores']}")
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)

    @discord.ui.button(label="الخريطة 🗺️", style=discord.ButtonStyle.blurple)
    async def map_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("مش لعبتك!", ephemeral=True)
            return
        u = await load_user_async(self.user_id)
        cur = u["worm_room"]
        desc = ""
        for i, r in enumerate(WORM_ROOMS):
            status = "✅" if i < cur else "📍" if i == cur else "🔒"
            desc += f"{status} {r['emoji']} **{r['name']}** - {r['desc']}\n"
        embed = discord.Embed(title="🗺️ خريطة عالم الدود", description=desc, color=0x00ff00)
        embed.add_field(name="انت هون", value=f"{WORM_ROOMS[cur]['emoji']} {WORM_ROOMS[cur]['name']}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="اهرب 🏃", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="هربت من عالم الدود! باي باي 👋", embed=None, view=None)

class BSFGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bsf", description="شوف قلوبك ودودك")
    async def bsf(self, interaction: discord.Interaction):
        await interaction.response.defer()
        u = await load_user_async(interaction.user.id)
        embed = discord.Embed(title=f"❤️ مملكة {interaction.user.display_name} 🪱", color=0xff69b4)
        embed.add_field(name="القلوب", value=f"{u['hearts']} ❤️", inline=True)
        embed.add_field(name="الدود", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="المنطقة", value=f"{WORM_ROOMS[u['worm_room']]['emoji']} {WORM_ROOMS[u['worm_room']]['name']}", inline=True)
        embed.add_field(name="استكشافات", value=f"{u['explores']}", inline=True)
        embed.set_footer(text="بهارتك يا موشي! انت ملك اللعاب")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="تحدي", description="تحدي الدود - لعبة الحظ")
    async def tahadi(self, interaction: discord.Interaction, رهان: int):
        await interaction.response.defer()
        if رهان <= 0:
            await interaction.followup.send("الرهان لازم اكبر من 0!", ephemeral=True)
            return
        u = await load_user_async(interaction.user.id)
        if u["hearts"] < رهان:
            await interaction.followup.send(f"ما معك قلوب كفاية! معك {u['hearts']}", ephemeral=True)
            return
        win = random.random() < 0.5
        if win:
            u["hearts"] += رهان
            msg = f"فزت! 🔥 +{رهان} قلوب\nبهارتك يا موشي!"
            color = 0xffa500
        else:
            u["hearts"] -= رهان
            msg = f"خسرت... -{رهان} قلوب\nالدود ضحك عليك 🪱"
            color = 0x808080
        await save_user_async(interaction.user.id, u)
        embed = discord.Embed(title="🎲 تحدي الدود", description=msg, color=color)
        embed.add_field(name="قلوبك هلا", value=f"{u['hearts']} ❤️")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="زعامة", description="لوحة الصدارة - مين ملك اللعاب؟")
    async def zaama(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        if redis_client:
            try:
                keys = await redis_client.keys("user:*")
                data = {}
                for k in keys[:100]:
                    uid = k.split(":")[1]
                    ud = await load_user_async(uid)
                    if ud["hearts"]>0 or ud["worms"]>0:
                        data[uid]=ud
            except: pass
        if not data:
            await interaction.followup.send("فش حدا لسه!", ephemeral=True)
            return
        sorted_hearts = sorted(data.items(), key=lambda x: x[1].get("hearts",0), reverse=True)[:5]
        sorted_worms = sorted(data.items(), key=lambda x: x[1].get("worms",0), reverse=True)[:5]
        embed = discord.Embed(title="👑 زعامة BSF", color=0xffd700)
        hearts_text = ""
        for i, (uid, ud) in enumerate(sorted_hearts, 1):
            try:
                user = await self.bot.fetch_user(int(uid))
                name = user.display_name
            except:
                name = f"لاعب {uid[:4]}"
            hearts_text += f"{i}. {name} - {ud.get('hearts',0)} ❤️\n"
        worms_text = ""
        for i, (uid, ud) in enumerate(sorted_worms, 1):
            try:
                user = await self.bot.fetch_user(int(uid))
                name = user.display_name
            except:
                name = f"لاعب {uid[:4]}"
            worms_text += f"{i}. {name} - {ud.get('worms',0)} 🪱\n"
        embed.add_field(name="❤️ ملوك القلوب", value=hearts_text or "فاضي", inline=False)
        embed.add_field(name="🪱 ملوك الدود", value=worms_text or "فاضي", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="هروب", description="اهرب وامسح بياناتك")
    async def horob(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        uid = str(interaction.user.id)
        if redis_client:
            try:
                await redis_client.delete(f"user:{uid}")
                await redis_client.delete(f"seen:{uid}")
            except: pass
        data = load_data()
        if uid in data:
            del data[uid]
            save_data(data)
        await interaction.followup.send("هربت ومسحت كل اشي! 🏃💨", ephemeral=True)

    @app_commands.command(name="لعبة", description="ادخل عالم الدود")
    async def le3ba(self, interaction: discord.Interaction):
        await interaction.response.defer()
        u = await load_user_async(interaction.user.id)
        room = WORM_ROOMS[min(u["worm_room"], len(WORM_ROOMS)-1)]
        embed = discord.Embed(
            title=f"🪱 عالم الدود - {room['emoji']} {room['name']}",
            description=f"{room['desc']}\n\n**{random.choice(BSF_LORE)}**\n\nدوس استكشاف!",
            color=0x8B4513
        )
        embed.add_field(name="دودك", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="قلوبك", value=f"{u['hearts']} ❤️", inline=True)
        await interaction.followup.send(embed=embed, view=WormView(interaction.user.id))

    @app_commands.command(name="خريطة", description="شوف خريطة عالم الدود كاملة")
    async def kharita(self, interaction: discord.Interaction):
        await interaction.response.defer()
        u = await load_user_async(interaction.user.id)
        cur = u["worm_room"]
        desc = ""
        for i, r in enumerate(WORM_ROOMS):
            status = "✅ مفتوحة" if i < cur else "📍 انت هون" if i == cur else "🔒 مقفولة"
            desc += f"**{i+1}. {r['emoji']} {r['name']}**\n{r['desc']}\n{status} - دود: {r['worms']} | حظ: {int(r['chance']*100)}%\n\n"
        embed = discord.Embed(title="🗺️ خريطة BSF الكاملة", description=desc, color=0x00ff00)
        embed.set_footer(text=f"استكشافاتك: {u['explores']} | بهارتك يا موشي!")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BSFGame(bot))
