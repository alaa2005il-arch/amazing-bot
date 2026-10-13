import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio

# حاول تشبك Redis - اذا فش، بستخدم ملف مؤقت
try:
    import redis.asyncio as redis
    REDIS_URL = os.getenv("REDIS_URL") or os.getenv("REDIS_PRIVATE_URL")
    redis_client = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None
except:
    redis_client = None

DATA_FILE = "bsf_data.json"

BAHARAT_LEVELS = [
    {"name": "ملح", "emoji": "🧂", "prize": 10},
    {"name": "كمون", "emoji": "🌿", "prize": 20},
    {"name": "فلفل", "emoji": "🌶️", "prize": 40},
    {"name": "كركم", "emoji": "💛", "prize": 80},
    {"name": "زعتر", "emoji": "🍃", "prize": 160},
    {"name": "قرفة", "emoji": "🪵", "prize": 320},
    {"name": "هيل", "emoji": "✨", "prize": 640},
    {"name": "زعفران", "emoji": "👑", "prize": 1250},
    {"name": "بهار سري", "emoji": "🔥", "prize": 2500},
    {"name": "بهارتك يا موشي", "emoji": "💎", "prize": 5000},
]

# 50 سؤال حقيقي - 5 لكل مستوى
QUESTIONS = [
    # مستوى 0 - ملح (سهل جدا)
    {"q": "عاصمة فلسطين؟", "options": ["القدس", "رام الله", "نابلس", "غزة"], "answer": 0, "level": 0, "type": "عام"},
    {"q": "كم عدد حروف اللغة العربية؟", "options": ["28", "26", "30", "24"], "answer": 0, "level": 0, "type": "عام"},
    {"q": "موشي فكر الدود ايش اول مرة؟", "options": ["معكرونة", "حبال", "خيطان", "سحالي"], "answer": 0, "level": 0, "type": "BSF"},
    {"q": "كم دودة في حفرة البداية؟", "options": ["28", "10", "50", "100"], "answer": 0, "level": 0, "type": "BSF"},
    {"q": "لون الملح؟", "options": ["ابيض", "اسود", "اخضر", "احمر"], "answer": 0, "level": 0, "type": "عام"},

    # مستوى 1 - كمون
    {"q": "شو يعني BSF؟", "options": ["Black Soldier Fly", "Best Spicy Food", "Be Strong Fast", "Baharat Super Fly"], "answer": 0, "level": 1, "type": "BSF"},
    {"q": "كم يوم في السنة؟", "options": ["365", "360", "300", "400"], "answer": 0, "level": 1, "type": "عام"},
    {"q": "اكبر محيط في العالم؟", "options": ["الهادئ", "الاطلسي", "الهندي", "المتجمد"], "answer": 0, "level": 1, "type": "عام"},
    {"q": "موسى اخو موشي تاع ايش؟", "options": ["الديسكورد", "الواتس", "الغسالة", "التلجرام"], "answer": 0, "level": 1, "type": "BSF"},
    {"q": "الكمون لونه؟", "options": ["بني مخضر", "احمر", "ازرق", "ابيض"], "answer": 0, "level": 1, "type": "عام"},

    # مستوى 2 - فلفل
    {"q": "اذا الدودة اكلت كمون شو بصير؟", "options": ["بتصير ذهبية", "بتنام", "بتهرب", "بتحكي"], "answer": 0, "level": 2, "type": "BSF"},
    {"q": "كم عدد قارات العالم؟", "options": ["7", "5", "6", "8"], "answer": 0, "level": 2, "type": "عام"},
    {"q": "عاصمة الاردن؟", "options": ["عمان", "اربد", "العقبة", "الزرقاء"], "answer": 0, "level": 2, "type": "عام"},
    {"q": "مين مخترع المصباح؟", "options": ["اديسون", "اينشتاين", "نيوتن", "تسلا"], "answer": 0, "level": 2, "type": "عام"},
    {"q": "الفلفل الحار فيه مادة اسمها؟", "options": ["كابسيسين", "كافيين", "نيكوتين", "جلوكوز"], "answer": 0, "level": 2, "type": "عام"},

    # مستوى 3 - كركم
    {"q": "عجيب النمر يطلع امتى؟", "options": ["لما تجاوب صح", "4:45 الفجر", "كل جمعة", "لما تبهّر"], "answer": 0, "level": 3, "type": "BSF"},
    {"q": "كم سن في فم الانسان البالغ؟", "options": ["32", "28", "30", "26"], "answer": 0, "level": 3, "type": "عام"},
    {"q": "اطول نهر في العالم؟", "options": ["النيل", "الفرات", "الامازون", "دجلة"], "answer": 0, "level": 3, "type": "عام"},
    {"q": "الكركم يستخرج من؟", "options": ["الجذور", "الاوراق", "البذور", "الازهار"], "answer": 0, "level": 3, "type": "عام"},
    {"q": "كم عدد الكواكب في المجموعة الشمسية؟", "options": ["8", "9", "7", "10"], "answer": 0, "level": 3, "type": "عام"},

    # مستوى 4 - زعتر
    {"q": "شو اسم مطبخ الخريطة؟", "options": ["مطبخ العمارة", "مطبخ موشي", "مطبخ الدود", "مطبخ BSF"], "answer": 0, "level": 4, "type": "BSF"},
    {"q": "الزعتر مفيد لايش؟", "options": ["المناعة", "النظر", "العظام", "كل ما سبق"], "answer": 3, "level": 4, "type": "عام"},
    {"q": "عاصمة لبنان؟", "options": ["بيروت", "طرابلس", "صيدا", "صور"], "answer": 0, "level": 4, "type": "عام"},
    {"q": "اسرع حيوان بري؟", "options": ["الفهد", "الاسد", "النمر", "الذئب"], "answer": 0, "level": 4, "type": "عام"},
    {"q": "كم قلب للاخطبوط؟", "options": ["3", "1", "2", "4"], "answer": 0, "level": 4, "type": "عام"},

    # مستوى 5 - قرفة
    {"q": "مين قال بهارتك يا موسى؟", "options": ["انت", "موشي", "عجيب", "الدودة"], "answer": 0, "level": 5, "type": "BSF"},
    {"q": "سرداب الاسرار فيه كم حظ؟", "options": ["70%", "45%", "85%", "15%"], "answer": 0, "level": 5, "type": "BSF"},
    {"q": "القرفة من وين بتيجي؟", "options": ["لحاء الشجر", "الورق", "البذور", "الجذر"], "answer": 0, "level": 5, "type": "عام"},
    {"q": "كم عظمة في جسم الانسان؟", "options": ["206", "200", "210", "196"], "answer": 0, "level": 5, "type": "عام"},
    {"q": "الدولة اللي اخترعت البارود؟", "options": ["الصين", "اليابان", "المانيا", "انجلترا"], "answer": 0, "level": 5, "type": "عام"},

    # مستوى 6 - هيل
    {"q": "معادلة BSF = ؟", "options": ["دود + بهار = فلوس", "غسالة + دود = عرش", "موشي + موسى = مشاهير", "كل ما سبق"], "answer": 3, "level": 6, "type": "BSF"},
    {"q": "الهيل يسمى ملكة التوابل صح؟", "options": ["صح", "خطأ، ملك", "خطأ، اميرة", "لا يوجد"], "answer": 0, "level": 6, "type": "عام"},
    {"q": "اكبر دولة عربية مساحة؟", "options": ["الجزائر", "السعودية", "مصر", "ليبيا"], "answer": 0, "level": 6, "type": "عام"},
    {"q": "ما هو الغاز الذي يتنفسه الانسان؟", "options": ["الاوكسجين", "الهيدروجين", "النيتروجين", "ثاني اكسيد الكربون"], "answer": 0, "level": 6, "type": "عام"},
    {"q": "كم لغة رسمية للامم المتحدة؟", "options": ["6", "5", "4", "8"], "answer": 0, "level": 6, "type": "عام"},

    # مستوى 7 - زعفران
    {"q": "ليش الزعفران غالي؟", "options": ["بده شغل يدوي كتير", "نادر", "بطلع مرة بالسنة", "كل ما سبق"], "answer": 3, "level": 7, "type": "عام"},
    {"q": "سعر كيلو الزعفران الاصلي تقريبا؟", "options": ["5000$+", "100$", "500$", "1000$"], "answer": 0, "level": 7, "type": "عام"},
    {"q": "BSF larvae بتعيش كم يوم؟", "options": ["14-18 يوم", "5 ايام", "30 يوم", "سنة"], "answer": 0, "level": 7, "type": "BSF"},
    {"q": "من وين اجت فكرة BSF اصلا؟", "options": ["تدوير النفايات العضوية", "صيد السمك", "اكل الطيور", "زينة"], "answer": 0, "level": 7, "type": "BSF"},
    {"q": "كم نسبة البروتين في دود BSF المجفف؟", "options": ["40-45%", "10%", "80%", "20%"], "answer": 0, "level": 7, "type": "BSF"},

    # مستوى 8 - بهار سري
    {"q": "لو بدك تصير مشهور BSF شو بتعمل؟", "options": ["بوت كل يوم", "ببهّر الدود", "بصور تيك توك", "كل ما سبق يا ملك"], "answer": 3, "level": 8, "type": "BSF"},
    {"q": "شو الفرق بين سرداب الاسرار وحفرة البداية؟", "options": ["الحظ والمخاطرة", "مافي فرق", "اللون", "عدد الدود"], "answer": 0, "level": 8, "type": "BSF"},
    {"q": "لو معك 1000 دودة BSF كم كيلو علف بتنتج باليوم؟", "options": ["يعتمد على الاكل", "كيلو ثابت", "10 كيلو", "صفر"], "answer": 0, "level": 8, "type": "BSF"},
    {"q": "شو هو frass؟", "options": ["سماد من فضلات BSF", "نوع دود", "مرض", "بهار"], "answer": 0, "level": 8, "type": "BSF"},
    {"q": "بهار سري = ؟", "options": ["خلطة موشي السرية", "ملح وفلفل", "كمون بس", "مافي بهار سري"], "answer": 0, "level": 8, "type": "BSF"},

    # مستوى 9 - بهارتك يا موشي (النهائي)
    {"q": "كم بهار في لعبة بهاراتك؟", "options": ["10", "5", "20", "100"], "answer": 0, "level": 9, "type": "BSF"},
    {"q": "اذا وصلت لهون شو انت؟", "options": ["بهارتك يا موشي 💎", "لسا ملح", "فلفل", "كمون"], "answer": 0, "level": 9, "type": "BSF"},
    {"q": "معادلة النجاح في BSF؟", "options": ["صبر + بهار + دود = عرش", "حظ بس", "فلوس بس", "غسالة"], "answer": 0, "level": 9, "type": "BSF"},
    {"q": "عجيب النمر شو بحكي لما تفوز؟", "options": ["الو بتقلو احسنت!", "مبروك", "برافو", "كلهم"], "answer": 0, "level": 9, "type": "BSF"},
    {"q": "اخر سؤال: بتحب بهاراتك؟", "options": ["اكيد يا ملك 🔥", "نص نص", "لا", "شو هاد"], "answer": 0, "level": 9, "type": "BSF"},
]

# ---- دوال التخزين Redis + fallback ----
async def load_user_data(uid: str):
    uid = str(uid)
    if redis_client:
        try:
            data = await redis_client.hgetall(f"user:{uid}")
            if data:
                # تحويل الارقام
                return {
                    "hearts": int(data.get("hearts", 0)),
                    "worms": int(data.get("worms", 0)),
                    "worm_room": int(data.get("worm_room", 0)),
                    "explores": int(data.get("explores", 0)),
                    "quiz_level": int(data.get("quiz_level", 0)),
                    "quiz_coins": int(data.get("quiz_coins", 0)),
                }
        except:
            pass
    # fallback ملف
    if not os.path.exists(DATA_FILE):
        return {"hearts":0,"worms":0,"worm_room":0,"explores":0,"quiz_level":0,"quiz_coins":0}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_data = json.load(f)
            return all_data.get(uid, {"hearts":0,"worms":0,"worm_room":0,"explores":0,"quiz_level":0,"quiz_coins":0})
    except:
        return {"hearts":0,"worms":0,"worm_room":0,"explores":0,"quiz_level":0,"quiz_coins":0}

async def save_user_data(uid: str, user_data: dict):
    uid = str(uid)
    if redis_client:
        try:
            await redis_client.hset(f"user:{uid}", mapping={k: str(v) for k, v in user_data.items()})
            return
        except:
            pass
    # fallback
    try:
        all_data = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        all_data[uid] = user_data
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    except:
        pass

async def get_unseen_question(uid: str, level: int):
    """جيب سؤال ما شافه المستخدم - seen:{user_id}"""
    uid = str(uid)
    # كل الاسئلة المتاحة لمستواه
    pool = [q for q in QUESTIONS if q["level"] <= level]
    if not pool:
        pool = QUESTIONS
    
    if redis_client:
        try:
            seen_key = f"seen:{uid}"
            seen = await redis_client.smembers(seen_key)
            available = [q for q in pool if q["q"] not in seen]
            if not available:
                await redis_client.delete(seen_key)
                available = pool
            q = random.choice(available)
            await redis_client.sadd(seen_key, q["q"])
            return q
        except:
            pass
    
    # fallback بدون seen
    return random.choice(pool)

# ---- View مع زر السؤال الجاي الاخضر ----
class QuizView(discord.ui.View):
    def __init__(self, user_id, question, level_idx, bot):
        super().__init__(timeout=20)
        self.user_id = user_id
        self.question = question
        self.level_idx = level_idx
        self.answered = False
        self.bot = bot
        for i, opt in enumerate(question["options"]):
            btn = discord.ui.Button(label=f"{opt[:80]}", style=discord.ButtonStyle.primary if i<2 else discord.ButtonStyle.secondary, custom_id=f"opt_{i}")
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, idx):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("مش دورك يا بهار! 😅", ephemeral=True)
                return
            if self.answered:
                return
            self.answered = True
            for child in self.children:
                child.disabled = True
            
            q = self.question
            bahar = BAHARAT_LEVELS[self.level_idx]
            correct = q["answer"] == idx
            user = await load_user_data(self.user_id)
            
            if correct:
                coins = bahar["prize"]
                user["quiz_coins"] = user.get("quiz_coins",0) + coins
                user["quiz_level"] = max(user.get("quiz_level",0), self.level_idx+1)
                await save_user_data(self.user_id, user)
                
                embed = discord.Embed(title=f"✅ صح! {bahar['emoji']} {bahar['name']}", color=0x00ff00)
                embed.description = f"**🐯 عجيب النمر:** الو بتقلو احسنت!\n\nربحت **{coins} عملة بهار**!\nمستواك: **{bahar['name']}**\nرصيدك: {user['quiz_coins']}"
                embed.set_footer(text="اضغط السؤال الجاي 👇")

                # زر اخضر للسؤال الجاي
                next_view = NextQuestionView(self.user_id, self.bot)
                await interaction.response.edit_message(embed=embed, view=next_view)
            else:
                correct_opt = q["options"][q["answer"]]
                embed = discord.Embed(title=f"❌ غلط يا بهار!", color=0xff0000)
                embed.description = f"**🐯 عجيب النمر:** غلطت 😿\n\nالصح: **{correct_opt}**\n\nجرب مرة تانية 👇"
                next_view = NextQuestionView(self.user_id, self.bot)
                await interaction.response.edit_message(embed=embed, view=next_view)
            self.stop()
        return callback

    async def on_timeout(self):
        self.answered = True
        for child in self.children:
            child.disabled = True

class NextQuestionView(discord.ui.View):
    def __init__(self, user_id, bot):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.bot = bot

    @discord.ui.button(label="السؤال الجاي 🌶️", style=discord.ButtonStyle.success, custom_id="next_q")
    async def next_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("مش دورك! اكتب /بهاراتك انت", ephemeral=True)
            return
        
        # defer عشان ما يصير App did not respond
        await interaction.response.defer()

        user = await load_user_data(self.user_id)
        current_level = user.get("quiz_level",0)
        if current_level >= 10:
            await interaction.followup.send(f"👑 {interaction.user.mention} خلصت كل البهارات! انت **بهارتك يا موشي**! 💎")
            return

        q = await get_unseen_question(self.user_id, current_level)
        bahar = BAHARAT_LEVELS[current_level]
        embed = discord.Embed(
            title=f"{bahar['emoji']} مستوى {current_level+1}: {bahar['name']} - {bahar['prize']} عملة",
            description=f"**🐯 عجيب النمر يسأل:**\n\n**{q['q']}**\n\nنوع: {q['type']} | معك 20 ثانية ⏱️",
            color=0xffd700
        )
        embed.set_footer(text=f"رصيدك: {user.get('quiz_coins',0)} | بهاراتك يا موشي!")
        view = QuizView(interaction.user.id, q, current_level, self.bot)
        await interaction.followup.send(embed=embed, view=view)

class BaharatGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="بهاراتك", description="لعبة سؤال وجواب - عجيب النمر يسأل")
    async def baharatak(self, interaction: discord.Interaction):
        # رد سريع عشان ما يصير App did not respond
        await interaction.response.defer()
        
        user = await load_user_data(interaction.user.id)
        current_level = user.get("quiz_level",0)
        
        if current_level >= 10:
            await interaction.followup.send(f"👑 {interaction.user.mention} خلصت كل البهارات! انت **بهارتك يا موشي**! رصيدك {user.get('quiz_coins',0)} 💎")
            return

        q = await get_unseen_question(interaction.user.id, current_level)
        bahar = BAHARAT_LEVELS[current_level]
        embed = discord.Embed(
            title=f"{bahar['emoji']} مستوى {current_level+1}: {bahar['name']} - {bahar['prize']} عملة",
            description=f"**🐯 عجيب النمر يسأل:**\n\n**{q['q']}**\n\nنوع: {q['type']} | معك 20 ثانية ⏱️",
            color=0xffd700
        )
        embed.set_footer(text=f"رصيدك: {user.get('quiz_coins',0)} | بهاراتك يا موشي!")
        view = QuizView(interaction.user.id, q, current_level, self.bot)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="رصيدي", description="شوف رصيدك بهارات + دود")
    async def rasedi(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await load_user_data(interaction.user.id)
        level_idx = min(user.get("quiz_level",0),9)
        level_name = BAHARAT_LEVELS[level_idx]["name"]
        level_emoji = BAHARAT_LEVELS[level_idx]["emoji"]
        rooms = ["حفرة البداية", "مغسلة الغسالات", "مطبخ العمارة", "سرداب الاسرار", "سطح القمر"]
        room_name = rooms[min(user.get("worm_room",0),4)]
        embed = discord.Embed(title=f"💰 رصيد {interaction.user.display_name}", color=0xffd700)
        embed.add_field(name="🪱 الدود", value=f"{user.get('worms',0)} دودة\n{room_name}", inline=True)
        embed.add_field(name="🧂 البهارات", value=f"{level_emoji} {level_name}\n{user.get('quiz_coins',0)} عملة", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="توب_بهارات", description="توب بهاراتك - مين اكثر واحد جمع؟")
    async def top_baharat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if redis_client:
            try:
                keys = await redis_client.keys("user:*")
                data = {}
                for k in keys[:50]:
                    uid = k.split(":")[1]
                    ud = await load_user_data(uid)
                    data[uid] = ud
            except:
                data = {}
        else:
            if not os.path.exists(DATA_FILE):
                await interaction.followup.send("لسة ما حد لعب!", ephemeral=True)
                return
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        if not data:
            await interaction.followup.send("لسة ما حد لعب!", ephemeral=True)
            return
        sorted_q = sorted(data.items(), key=lambda x: x[1].get("quiz_coins",0), reverse=True)[:10]
        text = "🏆 **توب بهاراتك**\n\n"
        for i, (uid, d) in enumerate(sorted_q, 1):
            if d.get("quiz_coins",0) == 0:
                continue
            try:
                user_obj = await self.bot.fetch_user(int(uid))
                name = user_obj.display_name
            except:
                name = f"لاعب {uid[:4]}"
            text += f"{i}. {name} - {d.get('quiz_coins',0)} عملة - {BAHARAT_LEVELS[min(d.get('quiz_level',0),9)]['name']}\n"
        await interaction.followup.send(text or "فش حدا لعب بهاراتك لسه! /بهاراتك")

# ==================== قصر هشام - المرحلة الأسطورية الجديدة ====================
HISHAM_LOCATIONS = {
    "القاعة الكبرى": {"emoji": "🏛️", "desc": "قاعة الأعمدة الحجرية"},
    "الحمام البارد": {"emoji": "❄️", "desc": "فسيفساء زرقاء"},
    "الحمام الدافئ": {"emoji": "🔥", "desc": "بخار وألغاز"},
    "غرفة شجرة الحياة": {"emoji": "🌳", "desc": "الفسيفساء الأسطورية - الكنز الحقيقي", "final": True},
}

HISHAM_PUZZLES = [
    {"q": "قصر هشام بني في أي عصر؟", "options": ["الأموي", "العباسي", "العثماني", "المملوكي"], "answer": 0, "reward": 100},
    {"q": "شجرة الحياة في قصر هشام فيها إيش؟", "options": ["أسد وغزال", "دود وبهار", "نمر وقط", "كل ما سبق"], "answer": 0, "reward": 150},
    {"q": "قصر هشام وين موجود؟", "options": ["أريحا", "القدس", "نابلس", "رام الله"], "answer": 0, "reward": 100},
    {"q": "كم قطعة فسيفساء في شجرة الحياة؟", "options": ["آلاف القطع", "10 قطع", "100 قطعة", "50 قطعة"], "answer": 0, "reward": 200},
]

class HishamPalaceView(discord.ui.View):
    def __init__(self, user_id, bot, stage=0):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bot = bot
        self.stage = stage

    @discord.ui.button(label="ادخل القاعة الكبرى 🏛️", style=discord.ButtonStyle.primary, row=0)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("مش دورك!", ephemeral=True)
            return
        await interaction.response.defer()
        puzzle = HISHAM_PUZZLES[self.stage]
        embed = discord.Embed(
            title=f"🏛️ قصر هشام - {list(HISHAM_LOCATIONS.keys())[self.stage]} {list(HISHAM_LOCATIONS.values())[self.stage]['emoji']}",
            description=f"**دودة البهار المرشدة 🧭:** وصلنا قصر هشام! {list(HISHAM_LOCATIONS.values())[self.stage]['desc']}\n\n**اللغز {self.stage+1}/4:** {puzzle['q']}\n",
            color=0xDAA520
        )
        view = HishamQuizView(self.user_id, self.bot, self.stage)
        for i, opt in enumerate(puzzle["options"]):
            view.add_item(HishamAnswerButton(i, opt, puzzle["answer"] == i, puzzle["reward"], self.stage))
        await interaction.followup.send(embed=embed, view=view)

class HishamAnswerButton(discord.ui.Button):
    def __init__(self, idx, label, is_correct, reward, stage):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.is_correct = is_correct
        self.reward = reward
        self.stage = stage
    async def callback(self, interaction: discord.Interaction):
        view: HishamQuizView = self.view
        if interaction.user.id != view.user_id:
            await interaction.response.send_message("مش دورك!", ephemeral=True)
            return
        if self.is_correct:
            user = await load_user_data(interaction.user.id)
            user["quiz_coins"] = user.get("quiz_coins",0) + self.reward
            await save_user_data(interaction.user.id, user)
            if self.stage >= 3:
                # النهاية الأسطورية
                embed = discord.Embed(
                    title="🏆🌳 أسطورة قصر هشام! شجرة الحياة!",
                    description=f"**أبو عيسى الأسد 🦁:** يا بطل! جمعت كل قطع الفسيفساء!\n\n**عجيب النمر 🐯:** شجرة الحياة اكتملت! الأسد يهاجم الغزال تحت الشجرة - رمز القوة!\n\n**دودة البهار 🧭:** أنت أول واحد يكتشف سر القصر منذ 1300 سنة!\n\n**الجائزة الكبرى:** +{self.reward} عملة + لقب **حارس قصر هشام** 👑\n\nرصيدك: {user['quiz_coins']} 💎\nبهارتك يا موشي!",
                    color=0xFFD700
                )
                file_path = "/mnt/data/gallery/hisham_palace_mosaic.png"
                files = []
                if os.path.exists(file_path):
                    files.append(discord.File(file_path, filename="hisham_mosaic.png"))
                    embed.set_image(url="attachment://hisham_mosaic.png")
                await interaction.response.edit_message(embed=embed, view=None)
                if files:
                    await interaction.followup.send(files=files)
            else:
                embed = discord.Embed(title=f"✅ صح! +{self.reward} عملة!", description=f"**المرحلة {self.stage+1} خلصت!**\n\n**المرشد:** ممتاز! تعال ندخل الغرفة الجاي!", color=0x00FF00)
                next_view = HishamPalaceView(interaction.user.id, view.bot, self.stage+1)
                await interaction.response.edit_message(embed=embed, view=next_view)
        else:
            await interaction.response.send_message("❌ غلط! جرب تاني - دودة البهار بتعطيك تلميح: فكر في أريحا! 🏜️", ephemeral=True)

class HishamQuizView(discord.ui.View):
    def __init__(self, user_id, bot, stage):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.bot = bot
        self.stage = stage

class HishamPalace(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="قصر_هشام", description="🏛️ مغامرة قصر هشام - شجرة الحياة الأسطورية في أريحا")
    async def hisham(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await load_user_data(interaction.user.id)
        embed = discord.Embed(
            title="🏛️ قصر هشام - Hisham's Palace - أريحا",
            description=f"**{interaction.user.mention} مرحبا في قصر هشام الأموي!**\n\n**القصة:** بعد ما هزمت ملك الدود 👑🐛 في Treasure Nook، دودة البهار المرشدة 🧭 قالتلك في كنز أكبر مخبى في **قصر هشام بأريحا**!\n\n**الكنز:** فسيفساء **شجرة الحياة** الأسطورية 🌳 - أسد يهاجم غزال تحت شجرة مزهرة - عمرها 1300 سنة!\n\n**المراحل:**\n🏛️ القاعة الكبرى - أعمدة حجرية\n❄️ الحمام البارد - فسيفساء زرقاء\n🔥 الحمام الدافئ - بخار وألغاز\n🌳 غرفة شجرة الحياة - النهاية الأسطورية!\n\n**شخصياتك:** عجيب 🐯، أبو عيسى 🦁، موسى 👦، دودة البهار 🐛 كلهم معك!\n\n**رصيدك:** {user.get('quiz_coins',0)} عملة\n\nاضغط ادخل لتبدأ!",
            color=0xDAA520
        )
        file_path = "/mnt/data/gallery/hisham_palace_mosaic.png"
        if os.path.exists(file_path):
            file = discord.File(file_path, filename="hisham_palace.png")
            embed.set_image(url="attachment://hisham_palace.png")
            view = HishamPalaceView(interaction.user.id, self.bot, 0)
            await interaction.followup.send(embed=embed, file=file, view=view)
        else:
            view = HishamPalaceView(interaction.user.id, self.bot, 0)
            await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BaharatGame(bot))
    await bot.add_cog(HishamPalace(bot))
