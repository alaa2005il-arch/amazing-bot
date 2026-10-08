import os
import random
import threading
import asyncio
from flask import Flask
import discord
from discord.ext import commands
from openai import OpenAI
from phrases import PHRASES, AI_SYSTEM
import yt_dlp
from discord import FFmpegPCMAudio

# سيرفر عشان Render ما يطفي
app = Flask(__name__)
@app.route('/')
def home():
    return "BSF Bot LIVE! احنا ال BSF احنا! 🔥"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

# اعداد الذكاء الاصطناعي
ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY")
)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# اعدادات الاغاني - هاي اللي كانت ناقصة
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'extract_flat': 'in_playlist',
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f"✅ BSF LIVE: {bot.user} - بيجيب اغاني كاملة!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    low = message.content.lower()
    if "bsf" in low:
        await message.channel.send(random.choice(PHRASES))
    await bot.process_commands(message)

@bot.command(name="موسى")
async def musa_ai(ctx, *, سوال: str = None):
    if not سوال:
        await ctx.send("هلا يا زعيم! اكتب سؤالك بعد!موسى")
        return
    async with ctx.typing():
        try:
            رد = ai_client.chat.completions.create(
                model="google/gemini-flash-1.5-8b:free",
                messages=[
                    {"role": "system", "content": AI_SYSTEM},
                    {"role": "user", "content": سوال}
                ]
            )
            await ctx.send(رد.choices[0].message.content[:2000])
        except Exception as e:
            print(f"AI Error: {e}")
            await ctx.send("المخ علق شوي يا زعيم، جرب كمان مرة! 🗑️")

# === اوامر الاغاني - هاد اللي كان ناقص ===
@bot.command(name="شغل")
async def play_song(ctx, *, query: str = None):
    if not query:
        return await ctx.send("اكتب اسم الاغنية! مثال:!شغل دحية BSF")
    if not ctx.author.voice:
        return await ctx.send("ادخل روم صوت اول يا زعيم!")

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

    async with ctx.typing():
        with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                url = info['url']
                title = info.get('title', query)
            except Exception as e:
                return await ctx.send(f"ما لقيت الاغنية: {e}")

        source = FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 **بشغل هسا:** {title}\nاحنا ال BSF احنا! 🔥")

@bot.command(name="اطلع")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت من الروم 🫡")
    else:
        await ctx.send("انا مش بالروم اصلا")

@bot.command(name="وقف")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("وقفت الاغنية ⏹️")

# تشغيل
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token.strip())
else:
    print("❌ DISCORD_TOKEN مش موجود")
