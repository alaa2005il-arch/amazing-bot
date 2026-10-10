import discord
from discord.ext import commands
import os
from game import load_data, save_data

data = load_data()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")
    await bot.tree.sync()
    print("Commands synced!")

@bot.tree.command(name="دود", description="دودة مشعة +3 ذهب")
async def dod(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in data:
        data[user_id] = {"gold": 0, "xp": 0}
    data[user_id]["gold"] += 3
    data[user_id]["xp"] += 56
    save_data(data)
    
    embed = discord.Embed(title="مكان رطب ومظلم", description=f"✨ دودة مشعة x1\n💰 +3 ذهب\n🪱 مجموع الدود: 28\n⭐ لفل: 1 | XP: 56", color=0x00ff00)
    embed.set_footer(text="Upstash Frankfurt | B.S.F ABO ISSA محظوظ لي")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
