import discord
from discord.ext import commands
from discord import app_commands
import random

# جرب نجيب phrases لو موجودة
try:
    from phrases import PHRASES
except:
    PHRASES = [
        "BSF بيحرس زعامة عجيب وأبو عيسى 🔥",
        "الزعامة لعجيب وبس 👑",
        "أبو عيسى الزعيم الحقيقي 💪",
        "البوت العجيب شغال! 🚀",
        "BSF لا ينام - يحرس الزعامة 24 ساعة"
    ]

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bsf", description="البوت العجيب - بيحرس زعامة عجيب وابو عيسى")
    async def bsf(self, interaction: discord.Interaction):
        phrase = random.choice(PHRASES)
        embed = discord.Embed(
            title="🔥 BSF البوت العجيب",
            description=f"**{phrase}**",
            color=discord.Color.gold()
        )
        embed.set_footer(text="يحرس زعامة عجيب وابو عيسى - BSF")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Game(bot))
