import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import datetime

DATA_FILE = "bsf_data.json"

# خريطة عالم الدود - بهارتك يا موشي
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
    "سر: في دودة ذهبية بتطلع بس الساعة 4:45 الفجر - نفس وقت ديبلوي تبعك!",
]

PHRASES = [
    "قلبك مليان دود يا وحش!",
    "دودة ورا دودة والقلوب بتزيد",
    "يا موشي انت ملك اللعاب رسمي!",
    "بهارتك يا موشي!",
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
        data[uid] = {
            "hearts": 0,
            "worms": 0,
            "worm_room": 0,
            "explores": 0,
            "last_daily": None,
            "inventory": []
        }
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
        
        data = load_data()
        u = data[str(self.user_id)]
        room = WORM_ROOMS[min(u["worm_room"], len(WORM_ROOMS)-1)]
        
        u["explores"] += 1
        roll = random.random()
        
        if roll < room["chance"]:
            found = room["worms"] + random.randint(0,2)
            # بهارتك - بونص عشوائي
            if random.random() < 0.15:
                found *= 2
                msg = f"**بهارتك يا موشي! 🔥** لقيت دودة مبهرة!\n+{found} دودات في {room['emoji']} {room['name']}"
            else:
                msg = f"لقيت {found} دودات في {room['emoji']} {room['name']}!\n{random.choice(PHRASES)}"
            
            u["worms"] += found
            u["hearts"] += found
            
            # ترقية الغرفة
            if u["explores"] % 5 == 0 and u["worm_room"] < len(WORM_ROOMS)-1:
                u["worm_room"] += 1
                msg += f"\n\n**فتحت منطقة جديدة!** ➡️ {WORM_ROOMS[u['worm_room']]['emoji']} {WORM_ROOMS[u['worm_room']]['name']}"
        else:
            # لور
            if random.random() < 0.5:
                msg = f"ما لقيت اشي... بس لقيت ورقة:\n> {random.choice(BSF_LORE)}"
            else:
                msg = f"فش دود في {room['name']}... الدود هرب! {room['emoji']}"

        save_data(data)
        
        embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=msg, color=0x8B4513)
        embed.add_field(name="دودك", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="قلوبك", value=f"{u['hearts']} ❤️", inline=True)
        embed.set_footer(text=f"استكشافات: {u['explores']}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="الخريطة 🗺️", style=discord.ButtonStyle.blurple)
    async def map_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("مش لعبتك!", ephemeral=True)
            return
        
        data = load_data()
        u = data[str(self.user_id)]
        cur = u["worm_room"]
        
        desc = ""
        for i, r in enumerate(WORM_ROOMS):
            status = "✅" if i < cur else "📍" if i == cur else "🔒"
            desc += f"{status} {r['emoji']} **{r['name']}** - {r['desc']}\n"
        
        embed = discord.Embed(title="🗺️ خريطة عالم الدود - بهارتك يا موشي", description=desc, color=0x00ff00)
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
        u = get_user(interaction.user.id)
        embed = discord.Embed(title=f"❤️ مملكة {interaction.user.display_name} 🪱", color=0xff69b4)
        embed.add_field(name="القلوب", value=f"{u['hearts']} ❤️", inline=True)
        embed.add_field(name="الدود", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="المنطقة", value=f"{WORM_ROOMS[u['worm_room']]['emoji']} {WORM_ROOMS[u['worm_room']]['name']}", inline=True)
        embed.add_field(name="استكشافات", value=f"{u['explores']}", inline=True)
        embed.set_footer(text="بهارتك يا موشي! انت ملك اللعاب")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="تحدي", description="تحدي الدود - لعبة الحظ")
    async def tahadi(self, interaction: discord.Interaction, رهان: int):
        if رهان <= 0:
            await interaction.response.send_message("الرهان لازم اكبر من 0!", ephemeral=True)
            return
        data = load_data()
        u = data[str(interaction.user.id)]
        if u["hearts"] < رهان:
            await interaction.response.send_message(f"ما معك قلوب كفاية! معك {u['hearts']}", ephemeral=True)
            return
        
        win = random.random() < 0.5
        if win:
            u["hearts"] += رهان
            msg = f"فزت! 🔥 +{رهان} قلوب\nبهارتك يا موشي!"
        else:
            u["hearts"] -= رهان
            msg = f"خسرت... -{رهان} قلوب\nالدود ضحك عليك 🪱"
        
        save_data(data)
        embed = discord.Embed(title="🎲 تحدي الدود", description=msg, color=0xffa500 if win else 0x808080)
        embed.add_field(name="قلوبك هلا", value=f"{u['hearts']} ❤️")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="زعامة", description="لوحة الصدارة - مين ملك اللعاب؟")
    async def zaama(self, interaction: discord.Interaction):
        data = load_data()
        if not data:
            await interaction.response.send_message("فش حدا لسه!", ephemeral=True)
            return
        
        sorted_hearts = sorted(data.items(), key=lambda x: x[1].get("hearts",0), reverse=True)[:5]
        sorted_worms = sorted(data.items(), key=lambda x: x[1].get("worms",0), reverse=True)[:5]
        
        embed = discord.Embed(title="👑 زعامة BSF - ملوك اللعاب", color=0xffd700)
        
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
        embed.set_footer(text="بهارتك يا موشي - انت الملك؟")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="هروب", description="اهرب من اللعبة وامسح بياناتك")
    async def horob(self, interaction: discord.Interaction):
        data = load_data()
        if str(interaction.user.id) in data:
            del data[str(interaction.user.id)]
            save_data(data)
            await interaction.response.send_message("هربت ومسحت كل اشي! 🏃💨", ephemeral=True)
        else:
            await interaction.response.send_message("انت مش باللعبة اصلا!", ephemeral=True)

    @app_commands.command(name="لعبة", description="ادخل عالم الدود - بهارتك يا موشي")
    async def le3ba(self, interaction: discord.Interaction):
        u = get_user(interaction.user.id)
        room = WORM_ROOMS[min(u["worm_room"], len(WORM_ROOMS)-1)]
        
        embed = discord.Embed(
            title=f"🪱 عالم الدود - {room['emoji']} {room['name']}",
            description=f"{room['desc']}\n\n**{random.choice(BSF_LORE)}**\n\nدوس استكشاف عشان تدور دود!",
            color=0x8B4513
        )
        embed.add_field(name="دودك", value=f"{u['worms']} 🪱", inline=True)
        embed.add_field(name="قلوبك", value=f"{u['hearts']} ❤️", inline=True)
        embed.add_field(name="منطقتك", value=f"{room['name']}", inline=True)
        embed.set_footer(text="ملك اللعاب موشي - بهارتك!")
        
        await interaction.response.send_message(embed=embed, view=WormView(interaction.user.id))

    @app_commands.command(name="خريطة", description="شوف خريطة عالم الدود كاملة")
    async def kharita(self, interaction: discord.Interaction):
        u = get_user(interaction.user.id)
        cur = u["worm_room"]
        desc = ""
        for i, r in enumerate(WORM_ROOMS):
            status = "✅ مفتوحة" if i < cur else "📍 انت هون" if i == cur else "🔒 مقفولة"
            desc += f"**{i+1}. {r['emoji']} {r['name']}**\n{r['desc']}\n{status} - دود: {r['worms']} | حظ: {int(r['chance']*100)}%\n\n"
        
        embed = discord.Embed(title="🗺️ خريطة BSF الكاملة", description=desc, color=0x00ff00)
        embed.set_footer(text=f"استكشافاتك: {u['explores']} | بهارتك يا موشي!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BSFGame(bot))
