import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os

# تخزين النقاط
DATA_FILE = "bsf_data.json"
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
    "اهرب من الغسالة! 🌀",
    "الثقب ظهر! مين بيلقطه أول؟ 🕳️"
]

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bsf", description="لعبة BSF - جمع قلوب الزعامة")
    async def bsf(self, interaction: discord.Interaction):
        data = load_data()
        user_id = str(interaction.user.id)

        if user_id not in data:
            data[user_id] = {"hearts": 0, "name": interaction.user.name}

        data[user_id]["hearts"] += 1
        save_data(data)

        embed = discord.Embed(
            title="❤️ جمعت قلب!",
            description=f"{interaction.user.mention} جمع قلب جديد!\n**{random.choice(PHRASES)}**\n\nعندك الآن **{data[user_id]['hearts']}** قلب",
            color=discord.Color.red()
        )
        embed.set_footer(text="يحرس زعامة عجيب وابو عيسى - BSF")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="تحدي", description="تحدي شخص على الزعامة")
    async def challenge(self, interaction: discord.Interaction, عضو: discord.Member):
        if عضو.id == interaction.user.id:
            await interaction.response.send_message("ما بتقدر تتحدى حالك! 😅", ephemeral=True)
            return

        winner = random.choice([interaction.user, عضو])
        embed = discord.Embed(
            title="⚔️ تحدي الزعامة!",
            description=f"{interaction.user.mention} تحدى {عضو.mention}\n\n🏆 الفائز هو **{winner.mention}**!\nزعامة BSF للأبد!",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="زعامة", description="شوف مين زعيم BSF الحالي")
    async def zaama(self, interaction: discord.Interaction):
        data = load_data()
        if not data:
            await interaction.response.send_message("لسا ما حدا جمع قلوب! كن أول زعيم بـ /bsf ❤️")
            return

        top = sorted(data.items(), key=lambda x: x[1]['hearts'], reverse=True)[:3]
        text = ""
        for i, (uid, info) in enumerate(top, 1):
            medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "❤️"
            text += f"{medal} <@{uid}> - {info['hearts']} قلب\n"

        embed = discord.Embed(
            title="👑 لوحة زعامة BSF",
            description=text,
            color=discord.Color.purple()
        )
        embed.set_footer(text="عجيب وابو عيسى - الزعماء المؤسسين")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="هروب", description="لعبة الهروب من الغسالة 🌀")
    async def escape(self, interaction: discord.Interaction):
        outcomes = [
            "نجحت تهرب من الغسالة! كاسر الغسالات ساعدك! 🎉",
            "الغسالة بلعتك! جرب مرة ثانية 😵‍💫🌀",
            "طلعت من الثقب الثاني! لقيت قلبين زيادة! ❤️❤️"
        ]
        result = random.choice(outcomes)

        data = load_data()
        user_id = str(interaction.user.id)
        if "لقيت قلبين" in result:
            if user_id not in data:
                data[user_id] = {"hearts": 0, "name": interaction.user.name}
            data[user_id]["hearts"] += 2
            save_data(data)

        await interaction.response.send_message(f"{interaction.user.mention} {result}")

async def setup(bot):
    await bot.add_cog(Game(bot))
