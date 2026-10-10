import os, json, random, traceback, discord, asyncio
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import requests

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL", "").strip().strip('"').strip("'")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip().strip('"').strip("'")
AI_KEY = os.getenv("OPENAI_API_KEY", "") or os.getenv("GROQ_API_KEY", "")

def upstash_command(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN: return None
    try:
        r = requests.post(UPSTASH_URL, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, json=list(args), timeout=10)
        return r.json().get("result")
    except: return None

DATA_FILE = "bsf_data.json"
def load_data():
    res = upstash_command("GET", "bsf_data")
    if res:
        try: return json.loads(res)
        except: pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: pass
    return {}

def save_data(data):
    try: upstash_command("SET", "bsf_data", json.dumps(data, ensure_ascii=False))
    except: pass
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

def get_user(uid):
    data = load_data(); uid = str(uid)
    if uid not in data:
        data[uid] = {"worms":0,"gold":0,"level":1,"xp":0,"worm_room":0,"explores":0,"inventory":[],"name":str(uid)}
        save_data(data)
    return data[uid], data

VIP_USERS = {
    "ابو عيسى": {"title": "👑 المؤسس", "color": 0xFF0000, "mult": 2},
    "عيسى": {"title": "👑 المؤسس", "color": 0xFF0000, "mult": 2},
    "موشي": {"title": "⚙️ المطور - ملك اللعاب", "color": 0x00FF00, "mult": 1.5},
    "موسى": {"title": "⚙️ المطور - بهارتك!", "color": 0x00FF00, "mult": 1.5},
    "عجيب": {"title": "🔥 عجيب BSF - دبل", "color": 0xFFD700, "mult": 2},
}
def get_vip_info(display_name):
    name_lower = display_name.lower()
    for key, info in VIP_USERS.items():
        if key.lower() in name_lower: return info
    return None

def ask_musa_ai(question):
    if AI_KEY:
        try:
            is_groq = AI_KEY.startswith("gsk_")
            url = "https://api.groq.com/openai/v1/chat/completions" if is_groq else "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "llama-3.1-8b-instant" if is_groq else "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "انت موسى، مساعد ذكي في سيرفر BSF، بتحكي فلسطيني عامي مضحك، بتحب الدود والاغاني، بهارتك يا موسى جملتك المشهورة، بتجاوب باختصار وبطريقة عجيبة."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 350
            }
            r = requests.post(url, headers=headers, json=data, timeout=15)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
        except Exception as e: print(f"AI Error: {e}")
    funny = [
        f"يا زلمة '{question}'؟ هاد بدو قعدة مع دودة ذهبية 👑 بهارتك يا موسى!",
        f"موسى بقول: '{question}'؟ اسال ابو عيسى هو بعرف 👑",
        f"'{question}' - روح شغل اغنية وانت بتحفر /دود 🪱🎵",
        f"بهارتك يا موسى! سؤالك '{question}' قوي زي دودة مشعة ✨",
    ]
    return random.choice(funny)

# ===== اغاني =====
music_queues = {}
def get_queue(guild_id):
    if guild_id not in music_queues: music_queues[guild_id] = []
    return music_queues[guild_id]

async def search_youtube(query):
    try:
        import yt_dlp
        ydl_opts = {'format': 'bestaudio', 'quiet': True, 'noplaylist': True, 'default_search': 'ytsearch1', 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info and info['entries']:
                v = info['entries'][0]
                return {'title': v.get('title'), 'url': v.get('webpage_url'), 'duration': v.get('duration'), 'thumbnail': v.get('thumbnail')}
    except Exception as e:
        print(f"YT Error: {e}")
    return {'title': query, 'url': f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}", 'duration': 0, 'thumbnail': None}

app = Flask('')
@app.route('/')
def home(): return "BSF BOT Online ♾️ DOD + AI + MUSIC + بهارتك - موسى"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
def keep_alive(): Thread(target=run_flask, daemon=True).start()

WORM_ROOMS = [
    {"id":0,"name":"حفرة البداية","emoji":"🕳️","desc":"مكان رطب ومظلم - بهارتك وين الطريق؟","chance":0.85,"worms":1,"color":0x8B4513},
    {"id":1,"name":"مغسلة الغسالات","emoji":"🌀","desc":"الدود مخبي جوا الجرابات","chance":0.70,"worms":2,"color":0x00BFFF},
    {"id":2,"name":"مطبخ العمارة","emoji":"🍝","desc":"بقايا أكل، جنة الدود الجوعان","chance":0.60,"worms":3,"color":0xFFA500},
    {"id":3,"name":"سرداب الاسرار","emoji":"📦","desc":"كراكيب BSF القديمة - هون اللور","chance":0.45,"worms":5,"color":0x800080},
    {"id":4,"name":"ثلاجة الموتى","emoji":"🧊","desc":"دود نادر وغالي، بدو قلب قوي","chance":0.30,"worms":8,"color":0xADD8E6},
    {"id":5,"name":"عرش BSF الذهبي","emoji":"👑","desc":"الزعيم الاخير - بهارتك يا موسى!","chance":0.15,"worms":15,"color":0xFFD700},
]
WORM_TYPES = [
    {"name":"دودة عادية","emoji":"🪱","value":1},
    {"name":"دودة مشعة - بهارتك!","emoji":"✨","value":3},
    {"name":"دودة ذهبية","emoji":"👑","value":10},
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} - BSF FULL READY - موسى')
    try: await bot.tree.sync(); print("SLASH SYNCED")
    except Exception as e: print(e)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"ERROR /{interaction.command.name}: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ صار ايرور بس البوت ما طفي ♾️", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ ايرور: {error}", ephemeral=True)
    except: pass

@bot.hybrid_command(name="دود", description="احفر ودور دود - بهارتك يا موسى")
@app_commands.choices(غرفة=[app_commands.Choice(name=f"{r['emoji']} {r['name']}", value=r['id']) for r in WORM_ROOMS])
async def worm_hunt(ctx, غرفة: int = 0):
    await ctx.defer()
    room = WORM_ROOMS[غرفة] if 0 <= غرفة < len(WORM_ROOMS) else WORM_ROOMS[0]
    user_data, all_data = get_user(ctx.author.id)
    user_data["name"] = ctx.author.display_name
    user_data["explores"] += 1
    vip = get_vip_info(ctx.author.display_name)

    if random.random() > room["chance"]:
        embed = discord.Embed(title=f"{room['emoji']} {room['name']}", description=f"{room['desc']}\n\n❌ **ما لقيت ولا دودة! هربت!**", color=room["color"])
        if vip: embed.set_author(name=f"{ctx.author.display_name} {vip['title']}")
        await ctx.send(embed=embed); save_data(all_data); return

    amount = random.randint(1, room["worms"])
    worm_type = random.choices(WORM_TYPES, weights=[70,20,10])[0]
    total = amount * worm_type["value"]
    mult = vip["mult"] if vip else 1
    total = int(total * mult)

    bonus = ""
    if random.random() < 0.15:
        total *= 2
        bonus = "\n🔥 **بهارتك يا موسى! دودة مبهرة دبل!**"

    user_data["worms"] += total; user_data["xp"] += total*2; user_data["gold"] += total
    if user_data["xp"] >= user_data["level"]*100: user_data["level"] += 1
    if user_data["explores"] % 5 == 0 and user_data["worm_room"] < len(WORM_ROOMS)-1:
        user_data["worm_room"] += 1

    save_data(all_data)
    color = vip["color"] if vip else room["color"]
    embed = discord.Embed(
        title=f"{room['emoji']} {room['name']} - لقيت دود! {vip['title'] if vip else ''}",
        description=f"{worm_type['emoji']} **{worm_type['name']}** x{amount}{bonus}\n💰 +{total} ذهب{' (x'+str(mult)+' 👑)' if mult>1 else ''}\n🪱 مجموع: {user_data['worms']} | ⭐ لفل {user_data['level']} | XP {user_data['xp']}",
        color=color
    )
    embed.set_footer(text=f"Upstash Frankfurt ♾️ | {ctx.author.display_name} | غرفتك: {WORM_ROOMS[user_data['worm_room']]['name']}")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="خريطة", description="خريطة عالم الدود")
async def kharita(ctx):
    await ctx.defer()
    user_data,_ = get_user(ctx.author.id)
    cur = user_data.get("worm_room",0)
    desc = ""
    for i, r in enumerate(WORM_ROOMS):
        status = "✅ مفتوحة" if i < cur else "📍 انت هون" if i == cur else "🔒 مقفولة"
        desc += f"**{i+1}. {r['emoji']} {r['name']}** - {status}\n{r['desc'][:40]} | حظ {int(r['chance']*100)}%\n\n"
    vip = get_vip_info(ctx.author.display_name)
    embed = discord.Embed(title="🗺️ خريطة BSF - بهارتك يا موسى", description=desc, color=vip["color"] if vip else 0x00ff00)
    embed.set_footer(text=f"استكشافات: {user_data.get('explores',0)} | كل 5 حفرات بتفتح غرفة")
    try:
        file = discord.File("worm_map.png", filename="map.png")
        embed.set_image(url="attachment://map.png")
        await ctx.send(embed=embed, file=file)
    except:
        await ctx.send(embed=embed)

@bot.hybrid_command(name="احصائيات", description="شوف احصائياتك")
async def stats(ctx):
    user_data,_ = get_user(ctx.author.id)
    vip = get_vip_info(ctx.author.display_name)
    embed = discord.Embed(title=f"📊 {ctx.author.display_name} {vip['title'] if vip else ''}", color=vip["color"] if vip else 0xFFD700)
    embed.add_field(name="🪱 دود", value=str(user_data.get("worms",0)), inline=True)
    embed.add_field(name="💰 ذهب", value=str(user_data.get("gold",0)), inline=True)
    embed.add_field(name="⭐ لفل", value=str(user_data.get("level",1)), inline=True)
    embed.add_field(name="✨ XP", value=str(user_data.get("xp",0)), inline=True)
    embed.add_field(name="🗺️ غرفتك", value=f"{WORM_ROOMS[user_data.get('worm_room',0)]['emoji']} {WORM_ROOMS[user_data.get('worm_room',0)]['name']}", inline=True)
    embed.add_field(name="🔍 حفرات", value=str(user_data.get("explores",0)), inline=True)
    if vip: embed.add_field(name="👑 الرتبة", value=f"{vip['title']} - x{vip['mult']} ذهب", inline=False)
    await ctx.send(embed=embed)

@bot.hybrid_command(name="توب", description="توب 10 صيادين الدود")
async def top_worms(ctx):
    await ctx.defer()
    data = load_data()
    if not data: await ctx.send("❌ لسه ما حدا جمع دود!"); return
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("worms",0), reverse=True)[:10]
    embed = discord.Embed(title="🏆 توب 10 BSF - ملوك اللعاب 🪱👑", color=0xFFD700)
    medals=["🥇","🥈","🥉"]; text=""
    for i,(uid,udata) in enumerate(sorted_users):
        name=udata.get("name",f"User {uid[:4]}"); worms=udata.get("worms",0); level=udata.get("level",1)
        vip = get_vip_info(name); vip_tag = f" {vip['title']}" if vip else ""
        medal=medals[i] if i<3 else f"**{i+1}**."; text+=f"{medal} **{name}**{vip_tag} - 🪱 {worms} | لفل {level}\n"
    embed.add_field(name="الترتيب", value=text, inline=False)
    embed.set_footer(text=f"لاعبين: {len(data)} | بهارتك يا موسى!")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="ليدربورد", description="نفس التوب")
async def leaderboard(ctx): await top_worms(ctx)

@bot.hybrid_command(name="بهار", description="بهارتك يا موسى!")
async def bahar(ctx):
    phrases = ["بهارتك يا موسى! 🔥","بهارتك يا موسى صارت حقيقة!","دودة ورا دودة والقلوب بتزيد","قلبك مليان دود يا وحش!","يا موشي انت ملك اللعاب رسمي!"]
    await ctx.send(random.choice(phrases))

@bot.hybrid_command(name="اسال", description="اسال موسى AI")
@app_commands.describe(سؤال="شو بدك تسال؟")
async def ask_cmd(ctx, سؤال: str):
    await ctx.defer()
    answer = ask_musa_ai(سؤال)
    embed = discord.Embed(title=f"🤖 موسى: {سؤال[:100]}", description=answer, color=0x00FF00)
    embed.set_footer(text=f"سأل: {ctx.author.display_name} | BSF AI | بهارتك يا موسى!")
    await ctx.send(embed=embed)

@bot.hybrid_command(name="موسى", description="احكي مع موسى")
@app_commands.describe(سؤال="سؤالك")
async def musa_cmd(ctx, سؤال: str): await ask_cmd(ctx, سؤال)

@bot.hybrid_command(name="اسال_موسى", description="اسال موسى AI")
@app_commands.describe(سؤال="سؤالك")
async def ask_musa2(ctx, سؤال: str): await ask_cmd(ctx, سؤال)

@bot.hybrid_command(name="شغل", description="شغل اغنية")
@app_commands.describe(اغنية="اسم الاغنية او رابط يوتيوب")
async def play_song(ctx, اغنية: str):
    await ctx.defer()
    result = await search_youtube(اغنية)
    q = get_queue(ctx.guild.id)
    q.append(result)
    embed = discord.Embed(title=f"🎵 {result['title'][:80]}", description=f"🔍 بحثت: **{اغنية}**\n\n🔗 {result['url']}\n\n{'✅ انضافت - رقم '+str(len(q))+' بالقائمة' if len(q)>1 else '▶️ جاهزة'}", color=0xFF0000)
    if result.get('thumbnail'): embed.set_thumbnail(url=result['thumbnail'])
    embed.set_footer(text=f"طلب: {ctx.author.display_name} | /اغاني للقائمة")
    await ctx.send(embed=embed)
    if ctx.author.voice and ctx.author.voice.channel and not ctx.guild.voice_client:
        try: await ctx.author.voice.channel.connect()
        except: pass

@bot.hybrid_command(name="اغنية", description="شغل اغنية")
@app_commands.describe(اغنية="اسم الاغنية")
async def song_cmd(ctx, اغنية: str): await play_song(ctx, اغنية)

@bot.hybrid_command(name="اغاني", description="قائمة الاغاني")
async def songs_list(ctx):
    q = get_queue(ctx.guild.id)
    if not q:
        embed = discord.Embed(title="🎵 القائمة فاضية", description="اكتب `/شغل اسم الاغنية`\nمثال: `/شغل عمرو دياب تملي معاك`", color=0xFF0000)
        await ctx.send(embed=embed); return
    text = ""
    for i, s in enumerate(q[:10], 1): text += f"**{i}.** {s['title'][:60]} - {s['url']}\n"
    embed = discord.Embed(title=f"🎵 قائمة الاغاني - {len(q)}", description=text, color=0xFF0000)
    await ctx.send(embed=embed)

@bot.hybrid_command(name="قائمة_الاغاني", description="قائمة الاغاني")
async def queue_list(ctx): await songs_list(ctx)

@bot.hybrid_command(name="وقف", description="وقف الاغاني")
async def stop_music(ctx):
    get_queue(ctx.guild.id).clear()
    if ctx.guild.voice_client:
        try: await ctx.guild.voice_client.disconnect()
        except: pass
    await ctx.send("⏹️ وقفت الاغاني ومسحت القائمة 🎵")

@bot.hybrid_command(name="سكب", description="سكب اغنية")
async def skip_song(ctx):
    q = get_queue(ctx.guild.id)
    if q: q.pop(0)
    if not q: await ctx.send("❌ ما في اغاني - اكتب `/شغل`")
    else:
        embed = discord.Embed(title=f"⏭️ سكبت - هلا: {q[0]['title'][:80]}", description=q[0]['url'], color=0xFF0000)
        await ctx.send(embed=embed)

@bot.hybrid_command(name="اوامر", description="كل الاوامر - دود + AI + اغاني")
async def awamer(ctx):
    embed = discord.Embed(title="🔥 BSF BOT - شغل موسى الكامل + بهارتك 🔥", description="""
**♾️ محفوظ في Upstash Frankfurt - شغل موسى**

**▬▬ 🎮 الدود ▬▬**
🪱 **/دود [الغرفة]** - احفر - بهارتك وين الطريق؟
🗺️ **/خريطة** - خريطة العوالم مع الصورة
📊 **/احصائيات** - رصيدك
🏆 **/توب** - توب 10 ملوك اللعاب
🧂 **/بهار** - بهارتك يا موسى!

**▬▬ 🤖 موسى AI ▬▬**
💬 **/اسال [سؤال]** - اسال موسى
🤖 **/موسى [سؤال]**

**▬▬ 🎵 اغاني ▬▬**
▶️ **/شغل [الاسم]** - شغل اغنية
📜 **/اغاني** - القائمة
⏭️ **/سكب** - سكب
⏹️ **/وقف** - وقف

**▬▬ 👑 الرتب ▬▬**
👑 **ابو عيسى** - المؤسس x2 ذهب
⚙️ **موشي** - ملك اللعاب x1.5
⚙️ **موسى** - بهارتك! x1.5
🔥 **عجيب** - عجيب BSF x1.2

**الغرف:** 🕳️ 85% | 🌀 70% | 🍝 60% | 📦 45% | 🧊 30% | 👑 15%
**الدود:** 🪱 1 | ✨ بهارتك! 3 | 👑 10

بهارتك يا موسى! 🪱🔥 - شغل موسى الاصلي
""", color=0xFFD700)
    await ctx.send(embed=embed)

keep_alive()
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD_BOT_TOKEN") or os.getenv("BOT_TOKEN")
if TOKEN: bot.run(TOKEN)
