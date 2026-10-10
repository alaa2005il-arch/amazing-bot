import os
import json
import random
import traceback
import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from flask import Flask
from threading import Thread
import requests

# ====== UPSTASH - الحفظ الدائم فرانكفورت ♾️ ======
UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").strip().strip('"').strip("'")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip().strip('"').strip("'")

def upstash_command(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        r = requests.post(
            UPSTASH_URL,
            headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"},
            json=list(args),
            timeout=10
        )
        j = r.json()
        return j.get("result")
    except Exception as e:
        print(f"Upstash error: {e}", flush=True)
        return None

DATA_FILE = "bsf_data.json"

def load_data():
    res = upstash_command("GET", "bsf_data")
    if res:
        try:
            return json.loads(res)
        except: pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}

def save_data(data):
    try:
        upstash_command("SET", "bsf_data", json.dumps(data, ensure_ascii=False))
    except Exception as e:
        print(f"save error: {e}")
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"worms": 0, "gold": 0, "level": 1, "xp": 0, "inventory": [], "last_hunt": None, "name": str(uid)}
        save_data(data)
    return data[uid], data

app = Flask('')
@app.route('/')
def home():
    return "BSF-BOT Online ♾️🪱 TOP"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run_flask, daemon=True).start()

WORM_ROOMS = [
    {"id": 0, "name": "حفرة البداية", "emoji": "🕳️", "desc": "مكان رطب ومظلم", "chance": 0.85, "worms": 1, "color": 0x8B4513},
    {"id": 1, "name": "مغسلة الغسالات", "emoji": "🌀", "desc": "الدود مخبي جوا الجرابات", "chance": 0.70, "worms": 2, "color": 0x00BFFF},
    {"id": 2, "name": "مطبخ العمارة", "emoji": "🍝", "desc": "بقايا أكل، جنة الدود", "chance": 0.60, "worms": 3, "color": 0xFFA500},
    {"id": 3, "name": "سرداب الاسرار", "emoji": "📦", "desc": "كراكيب BSF القديمة", "chance": 0.45, "worms": 5, "color": 0x800080},
    {"id": 4, "name": "ثلاجة الموتى", "emoji": "🧊", "desc": "دود نادر وغالي", "chance": 0.30, "worms": 8, "color": 0xADD8E6},
    {"id": 5, "name": "عرش BSF الذهبي", "emoji": "👑", "desc": "دودة ذهبية ♾️", "chance": 0.15, "worms": 15, "color": 0xFFD700},
]

WORM_TYPES = [
    {"name": "دودة عادية", "emoji": "🪱", "value": 1},
    {"name": "دودة مشعة", "emoji": "✨", "value": 3},
    {"name": "دودة ذهبية", "emoji": "👑", "value": 10},
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} - BSF شغال ♾️ TOP READY')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e: print(e)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"ERROR in /{interaction.command.name}: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ صار ايرور: {error}\nبس البوت ما طفي ♾️", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ صار ايرور: {error}", ephemeral=True)
    except: pass

@bot.hybrid_command(name="دود", description="احفر ودور دود")
@app_commands.choices(غرفة=[app_commands.Choice(name=f"{r['emoji']} {r['name']}", value=r['id']) for r in WORM_ROOMS])
async def worm_hunt(ctx, غرفة: int = 0):
    try:
        await ctx.defer()
        room = WORM_ROOMS[غرفة] if 0 <= غرفة < len(WORM_ROOMS) else WORM_ROOMS[0]
        user_data, all_data = get_user(ctx.author.id)
        user_data["name"] = ctx.author.display_name

        if random.random() > room["chance"]:
            embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=f"{room['desc']}\n\n❌ **ما لقيت ولا دودة!**\nحاول مرة تانية 🕳️", color=room["color"])
            await ctx.send(embed=embed)
            save_data(all_data)
            return

        amount = random.randint(1, room["worms"])
        worm_type = random.choices(WORM_TYPES, weights=[70, 20, 10])[0]
        total_worms = amount * worm_type["value"]

        user_data["worms"] += total_worms
        user_data["xp"] += total_worms * 2
        user_data["gold"] += total_worms
        if user_data["xp"] >= user_data["level"] * 100:
            user_data["level"] += 1

        save_data(all_data)

        embed = discord.Embed(
            title=f"{room['emoji']} {room['name']} - لقيت دود!",
            description=f"{room['desc']}\n\n{worm_type['emoji']} **{worm_type['name']}** x{amount}\n💰 +{total_worms} ذهب\n🪱 مجموع الدود: {user_data['worms']}\n⭐ لفل: {user_data['level']} | XP: {user_data['xp']}",
            color=room["color"]
        )
        embed.set_footer(text=f"محفوظ في Upstash Frankfurt ♾️ | {ctx.author.display_name}")
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error in worm_hunt: {e}")
        traceback.print_exc()
        try: await ctx.send(f"❌ ايرور: {e}", ephemeral=True)
        except: pass

@bot.hybrid_command(name="احصائيات", description="شوف احصائياتك")
async def stats(ctx):
    user_data, _ = get_user(ctx.author.id)
    embed = discord.Embed(title=f"📊 احصائيات {ctx.author.display_name}", color=0xFFD700)
    embed.add_field(name="🪱 دود", value=str(user_data.get("worms", 0)), inline=True)
    embed.add_field(name="💰 ذهب", value=str(user_data.get("gold", 0)), inline=True)
    embed.add_field(name="⭐ لفل", value=str(user_data.get("level", 1)), inline=True)
    embed.add_field(name="✨ XP", value=str(user_data.get("xp", 0)), inline=True)
    embed.set_footer(text="محفوظ للأبد في Upstash ♾️")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="توب", description="توب 10 اكثر ناس جمعو دود 🪱👑")
async def top_worms(ctx):
    try:
        await ctx.defer()
        data = load_data()
        if not data:
            await ctx.send("❌ لسه ما حدا جمع دود!")
            return

        # ترتيب حسب الدود
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("worms", 0), reverse=True)[:10]

        embed = discord.Embed(title="🏆 توب 10 صيادين الدود BSF 👑🪱", description="اكثر ناس جمعو دود في السيرفر", color=0xFFD700)
        
        medals = ["🥇", "🥈", "🥉"]
        text = ""
        for i, (uid, udata) in enumerate(sorted_users):
            name = udata.get("name", f"User {uid[:4]}")
            worms = udata.get("worms", 0)
            level = udata.get("level", 1)
            medal = medals[i] if i < 3 else f"**{i+1}**."
            text += f"{medal} **{name}** - 🪱 {worms} | ⭐ لفل {level}\n"

        embed.add_field(name="الترتيب", value=text or "لا يوجد بيانات", inline=False)
        embed.set_footer(text=f"مجموع اللاعبين: {len(data)} | محفوظ في Upstash Frankfurt ♾️")
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Error in top: {e}")
        traceback.print_exc()
        await ctx.send(f"❌ ايرور في التوب: {e}")

@bot.hybrid_command(name="ليدربورد", description="نفس التوب بس بالانجليزي")
async def leaderboard(ctx):
    await top_worms(ctx)

keep_alive()
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN") or os.getenv("BOT_TOKEN")
if not TOKEN:
    import time
    while True: time.sleep(3600)
else:
    bot.run(TOKEN)
