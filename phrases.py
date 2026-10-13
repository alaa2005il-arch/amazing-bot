import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os

BAHARAT_EMOJI = "🧂"
DATA_FILE = "users_data.json"

QUESTIONS = [
    {"question": "ما هي البهارات الأساسية للمنسف؟", "options": ["كركم وكمون", "بهار حلو وهيل", "فلفل أسود وملح", "زعتر وسماق"], "correct": 1, "level": 0},
    {"question": "شو أكثر بهار بستخدموه في الزعتر الفلسطيني؟", "options": ["قرفة", "سمسم", "زعتر بري", "كراوية"], "correct": 2, "level": 1},
]

def load_all_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_all_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def load_user_data(user_id):
    data = load_all_data()
    return data.get(str(user_id), {"quiz_coins": 0, "quiz_level": 0})

async def save_user_data(user_id, user_data):
    data = load_all_data()
    data[str(user_id)] = user_data
    save_all_data(data)

class BaharatGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="بهاراتك", description="اختبر معلوماتك عن البهارات")
    async def baharat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await load_user_data(interaction.user.id)
        lvl = min(user.get("quiz_level", 0), 9)
        q = random.choice([x for x in QUESTIONS if x.get("level", 0) <= lvl])

        embed = discord.Embed(title=f"{BAHARAT_EMOJI} {q['question']}", color=0xF4A460)
        view = discord.ui.View(timeout=60)
        correct_idx = q["correct"]

        for i, opt in enumerate(q["options"]):
            btn = discord.ui.Button(label=opt, style=discord.ButtonStyle.secondary, custom_id=f"opt_{i}")
            async def cb(inter: discord.Interaction, correct=(i == correct_idx), chosen_label=opt):
                if inter.user.id != interaction.user.id:
                    await inter.response.send_message("هذا السؤال ليس لك!", ephemeral=True)
                    return

                for child in view.children:
                    child.disabled = True
                    if child.custom_id == f"opt_{correct_idx}":
                        child.style = discord.ButtonStyle.success
                    elif child.label == chosen_label and not correct:
                        child.style = discord.ButtonStyle.danger

                if correct:
                    u = await load_user_data(inter.user.id)
                    u["quiz_coins"] = u.get("quiz_coins", 0) + 10
                    u["quiz_level"] = min(u.get("quiz_level", 0) + 1, 9)
                    await save_user_data(inter.user.id, u)
                    await inter.response.edit_message(content=f"✅ صح! **{chosen_label}** +10 عملات", embed=None, view=view)
                else:
                    await inter.response.edit_message(content=f"❌ غلط! الصح هو **{q['options'][correct_idx]}**", embed=None, view=view)

            btn.callback = cb
            view.add_item(btn)

        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BaharatGame(bot))
