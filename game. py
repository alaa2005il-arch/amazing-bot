import discord
from discord.ext import commands

class BSFGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="bsf", description="لعبة كهف BSF")
    async def bsf(self, interaction: discord.Interaction):
        await interaction.response.send_message("مرحبا بك في كهف BSF - مغامرة الزعامة!")

async def setup(bot):
    await bot.add_cog(BSFGame(bot))
