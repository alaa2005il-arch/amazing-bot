import os
import random
import asyncio
import threading
from flask import Flask
import discord
from discord.ext import commands
from openai import OpenAI
from phrases import PHRASES, AI_SYSTEM
import yt_dlp
from discord import FFmpegPCMAudio

app = Flask(__name__)
@app.route('/')
def home():
    return "BSF Bot LIVE! احنا ال BSF احنا! 🔥"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_web, daemon=True).start()

ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY")
)

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'no_warnings': True,
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.event
async def on_ready():
    print(f"✅ BSF LIVE: {bot.user}")

@bot.event
async def setup_hook():
    try:
        await bot.load_extension("game")
        print("✅ Game loaded!")
    except Exception as e:
        print(f"Game Error: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    low = message.content.lower()
    if "bsf" in low:
        await message.channel.send(random.choice(PHRASES))
    await bot.process_commands(message)

def get_audio_url(query):
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
        search = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if not search['entries']:
            return None, None
        video = search['entries'][0]
        info = ydl.extract_info(video['webpage_url'], download=False)
        return info['url'], info.get('title', query)

@bot.command(name="موسى")
async def musa_ai(ctx, *, سوال: str = None):
    if not سوال:
        await ctx.send("هلا يا زعيم! اكتب سؤالك بعد!موسى")
        return
    async with ctx.typing():
        try:
            loop = asyncio.get_event_loop()
            رد = await loop.run_in_executor(None, lambda: ai_client.chat.completions.create(
                model="google/gemini-flash-1.5-8b:free",
                messages=[{"role": "system", "content": AI_SYSTEM},{"role": "user", "content": سوال}]
            ))
            await ctx.send(رد.choices[0].message.content[:2000])
        except Exception as e:
            print(f"AI Error: {e}")
            await ctx.send("المخ علق شوي يا زعيم، جرب كمان مرة! 🗑️")

@bot.command(name="شغل")
async def play_song(ctx, *, query: str = None):
    if not query:
        return await ctx.send("اكتب اسم الاغنية! مثال:!شغل دحية BSF")
    if not ctx.author.voice:
        return await ctx.send("ادخل روم صوت اول يا زعيم!")

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    async with ctx.typing():
        try:
            loop = asyncio.get_event_loop()
            url, title = await loop.run_in_executor(None, lambda: get_audio_url(query))

            if not url:
                return await ctx.send("ما لقيت الاغنية")

            source = FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f"🎶 **بشغل هسا:** {title}")
        except Exception as e:
            print(f"Play Error: {e}")
            await ctx.send(f"خطأ بالتشغيل: {e}")

@bot.command(name="اطلع")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("طلعت 🫡")

@bot.command(name="وقف")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("وقفت ⏹️")

token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token.strip())
