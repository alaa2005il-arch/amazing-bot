import discord
from discord.ext import commands
import random

class BSFGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="bsf", description="ابدأ لعبة BSF")
    async def bsf(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔥 BSF GAME - Black Survival Filter",
            description="**اختر شخصيتك وابدأ القتال!**\n\n🎮 اللعبة جاهزة\n⚔️ اضغط Start للبدء\n\nالمطور: Alaa",
            color=discord.Color.red()
        )
        embed.set_footer(text="BSF Live | Ready to Fight!")

        view = discord.ui.View()
        btn = discord.ui.Button(label="Start Game 🎮", style=discord.ButtonStyle.green)

        async def btn_callback(interaction2):
            await interaction2.response.send_message(
                f"🔥 أهلا {interaction2.user.mention}! اللعبة بدأت!\n"
                f"❤️ HP: 100 | ⚔️ ATK: 25 | 🛡️ DEF: 15\n"
                f"استخدم /bsf مرة ثانية لإعادة اللعب!",
                ephemeral=True
            )

        btn.callback = btn_callback
        view.add_item(btn)

        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BSFGame(bot))
