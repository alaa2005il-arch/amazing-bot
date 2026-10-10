import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio

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

QUESTIONS = [
    {"q": "موشي فكر الدود ايش اول مرة؟", "options": ["معكرونة", "حبال", "سحالي", "خيطان"], "answer": 0, "level": 0, "type": "BSF"},
    {"q": "كم دودة في حفرة البداية؟", "options": ["28", "10", "50", "15"], "answer": 0, "level": 0, "type": "BSF"},
    {"q": "شو يعني BSF؟", "options": ["Black Soldier Fly", "Best Spicy Food", "Be Strong Fast", "Baharat Super Fly"], "answer": 0, "level": 1, "type": "BSF"},
    {"q": "عاصمة فلسطين؟", "options": ["القدس", "رام الله", "أريحا", "غزة"], "answer": 0, "level": 1, "type": "عام"},
    {"q": "موسى اخو موشي تاع ايش؟", "options": ["الواتس", "الديسكورد", "الغسالة", "الدود"], "answer": 0, "level": 2, "type": "BSF"},
    {"q": "اذا الدودة اكلت كمون شو بصير؟", "options": ["بتصير ذهبية", "بتنام", "بتهرب", "بتحكي"], "answer": 0, "level": 2, "type": "BSF"},
    {"q": "عجيب النمر يطلع امتى؟", "options": ["لما تجاوب صح", "4:45 الفجر", "كل جمعة", "لما تبهّر"], "answer": 0, "level": 3, "type": "BSF"},
    {"q": "كم سن في فم الانسان؟", "options": ["32", "28", "30", "26"], "answer": 0, "level": 3, "type": "عام"},
    {"q": "شو اسم مطبخ الخريطة؟", "options": ["مطبخ العمارة", "مطبخ موشي", "مطبخ الدود", "مطبخ BSF"], "answer": 0, "level": 4, "type": "BSF"},
    {"q": "مين قال بهارتك يا موسى؟", "options": ["انت", "موشي", "عجيب", "الدودة"], "answer": 0, "level": 5, "type": "BSF"},
    {"q": "سرداب الاسرار فيه كم حظ؟", "options": ["45%", "85%", "70%", "15%"], "answer": 0, "level": 5, "type": "BSF"},
    {"q": "معادلة BSF = ؟", "options": ["دود + بهار = فلوس", "غسالة + دود = عرش", "موشي + موسى = مشاهير", "كل ما سبق"], "answer": 3, "level": 6, "type": "BSF"},
    {"q": "لو بدك تصير مشهور BSF شو بتعمل؟", "options": ["بوت كل يوم", "ببهّر الدود", "بصور تيك توك", "كل ما سبق يا ملك"], "answer": 3, "level": 8, "type": "BSF"},
    {"q": "كم بهار في لعبة بهاراتك؟", "options": ["10", "5", "20", "100"], "answer": 0, "level": 9, "type": "BSF"},
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_quiz_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"hearts":0,"worms":0,"worm_room":0,"explores":0,"last_daily":None,"inventory":[],"quiz_level":0,"quiz_coins":0}
    if "quiz_level" not in data[uid]:
        data[uid]["quiz_level"] = 0
        data[uid]["quiz_coins"] = 0
        save_data(data)
    return data[uid], data

class QuizView(discord.ui.View):
    def __init__(self, user_id, question, level_idx):
        super().__init__(timeout=15)
        self.user_id = user_id
        self.question = question
        self.level_idx = level_idx
        self.answered = False
        for i, opt in enumerate(question["options"]):
            btn = discord.ui.Button(label=f"{opt[:80]}", style=discord.ButtonStyle.primary if i<2 else discord.ButtonStyle.secondary, custom_id=str(i))
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
            all_data = load_data()
            uid_str = str(self.user_id)
            user = all_data.get(uid_str, {})
            
            if correct:
                coins = bahar["prize"]
                user["quiz_coins"] = user.get("quiz_coins",0) + coins
                user["quiz_level"] = max(user.get("quiz_level",0), self.level_idx+1)
                all_data[uid_str] = user
                save_data(all_data)
                
                embed = discord.Embed(title=f"✅ صح! {bahar['emoji']} {bahar['name']}", color=0x00ff00)
                embed.description = f"**🐯 عجيب النمر:** الو بتقلو احسنت!\n\nربحت **{coins} عملة بهار**!\nمستواك: **{bahar['name']}**\nرصيدك: {user['quiz_coins']}"
                embed.set_footer(text="اكتب /بهاراتك للسؤال الجاي - الصعوبة بتزيد!")
            else:
                correct_opt = q["options"][q["answer"]]
                embed = discord.Embed(title=f"❌ او جواب خطاء لما يغلط!", color=0xff0000)
                embed.description = f"**🐯 عجيب النمر:** غلطت يا بهار 😿\n\nالصح: **{correct_opt}**"

            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()
        return callback

class BaharatGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="بهاراتك", description="لعبة سؤال وجواب - عجيب النمر يسأل")
    async def baharatak(self, interaction: discord.Interaction):
        all_data = load_data()
        uid_str = str(interaction.user.id)
        user = all_data.get(uid_str, {"quiz_level":0,"quiz_coins":0,"hearts":0,"worms":0,"worm_room":0,"explores":0})
        current_level = user.get("quiz_level",0)
        
        if current_level >= 10:
            await interaction.response.send_message(f"👑 {interaction.user.mention} خلصت كل البهارات! انت **بهارتك يا موشي**! رصيدك {user.get('quiz_coins',0)} 💎")
            return

        level_questions = [q for q in QUESTIONS if q["level"] <= current_level]
        if not level_questions:
            level_questions = QUESTIONS
        q = random.choice(level_questions)
        bahar = BAHARAT_LEVELS[current_level]

        embed = discord.Embed(
            title=f"{bahar['emoji']} مستوى {current_level+1}: {bahar['name']} - {bahar['prize']} عملة",
            description=f"**🐯 عجيب النمر يسأل:**\n\n**{q['q']}**\n\nنوع: {q['type']} | معك 15 ثانية ⏱️",
            color=0xffd700
        )
        embed.set_footer(text=f"رصيدك: {user.get('quiz_coins',0)} | بهاراتك يا موشي!")

        view = QuizView(interaction.user.id, q, current_level)
        await interaction.response.send_message(embed=embed, view=view)
        
        # تايمر - بعد 15 ثانية
        await asyncio.sleep(15)
        if not view.answered:
            for child in view.children:
                child.disabled = True
            timeout_embed = discord.Embed(title="⏰ خلص الوقت!", description=f"الجواب: **{q['options'][q['answer']]}**\nجرب /بهاراتك مرة تانية", color=0x808080)
            try:
                await interaction.edit_original_response(embed=timeout_embed, view=view)
            except:
                pass

    @app_commands.command(name="رصيدي", description="شوف رصيدك بهارات + دود")
    async def rasedi(self, interaction: discord.Interaction):
        all_data = load_data()
        user = all_data.get(str(interaction.user.id), {"quiz_level":0,"quiz_coins":0,"worms":0,"worm_room":0})
        level_name = BAHARAT_LEVELS[min(user.get("quiz_level",0),9)]["name"]
        rooms = ["حفرة البداية", "مغسلة الغسالات", "مطبخ العمارة", "سرداب الاسرار", "سطح القمر"]
        room_name = rooms[min(user.get("worm_room",0),4)]
        embed = discord.Embed(title=f"💰 رصيد {interaction.user.display_name}", color=0xffd700)
        embed.add_field(name="🪱 الدود", value=f"{user.get('worms',0)} دودة\n{room_name}", inline=True)
        embed.add_field(name="🧂 البهارات", value=f"{level_name}\n{user.get('quiz_coins',0)} عملة", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="توب_بهارات", description="توب بهاراتك - مين اكثر واحد جمع؟")
    async def top_baharat(self, interaction: discord.Interaction):
        data = load_data()
        if not data:
            await interaction.response.send_message("لسة ما حد لعب!", ephemeral=True)
            return
        sorted_q = sorted(data.items(), key=lambda x: x[1].get("quiz_coins",0), reverse=True)[:10]
        text = "🏆 **توب بهاراتك**\n\n"
        for i, (uid, d) in enumerate(sorted_q, 1):
            if d.get("quiz_coins",0) == 0:
                continue
            try:
                user = await self.bot.fetch_user(int(uid))
                name = user.display_name
            except:
                name = f"لاعب {uid[:4]}"
            text += f"{i}. {name} - {d.get('quiz_coins',0)} عملة - {BAHARAT_LEVELS[min(d.get('quiz_level',0),9)]['name']}\n"
        await interaction.response.send_message(text or "فش حدا لعب بهاراتك لسه! /بهاراتك")

async def setup(bot):
    await bot.add_cog(BaharatGame(bot))
