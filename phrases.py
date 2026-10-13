# BSF Bot - بهارتي + كنز متحرك + قصر هشام + أصوات - النسخة المدمجة النهائية
# المطور: BSF Team - للصق المباشر في amazing-bot/baharat.py
# انسخ هذا الملف كامل وضعه في GitHub Repo: amazing-bot/baharat.py

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio
from typing import Optional, List, Dict, Tuple

# --- إعداد Redis الاختياري ---
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

DATA_FILE = "baharat_data.json"
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_KEY = "bsf:baharat:users"

redis_client = None
if REDIS_AVAILABLE and REDIS_URL:
    try:
        redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    except Exception:
        redis_client = None

# === BAHARAT_LEVELS - 10 مستويات بهارات ===
BAHARAT_LEVELS = [
    {"id": 0, "name": "ملح", "emoji": "🧂", "prize": 10, "color": 0xFFFFFF, "desc": "البداية - أساس كل شيء"},
    {"id": 1, "name": "كمون", "emoji": "🌿", "prize": 25, "color": 0x8B7355, "desc": "نكهة الأرض"},
    {"id": 2, "name": "فلفل", "emoji": "🌶️", "prize": 50, "color": 0xFF4444, "desc": "الحرارة تبدأ"},
    {"id": 3, "name": "كزبرة", "emoji": "🍃", "prize": 75, "color": 0x4CAF50, "desc": "عطر فلسطين"},
    {"id": 4, "name": "زعتر", "emoji": "🌱", "prize": 100, "color": 0x7CB342, "desc": "زعتر بلادي"},
    {"id": 5, "name": "قرفة", "emoji": "🪵", "prize": 150, "color": 0xA0522D, "desc": "دفء الشتاء"},
    {"id": 6, "name": "هيل", "emoji": "🫘", "prize": 200, "color": 0x9CCC65, "desc": "قهوة العرب"},
    {"id": 7, "name": "قرنفل", "emoji": "🌸", "prize": 300, "color": 0x8D6E63, "desc": "سر العطارة"},
    {"id": 8, "name": "زعفران", "emoji": "💛", "prize": 500, "color": 0xFFD700, "desc": "ذهب المطبخ"},
    {"id": 9, "name": "بهارتك يا موشي", "emoji": "👑", "prize": 1000, "color": 0xFF6B2D, "desc": "التاج النهائي - أسطورة BSF"},
]

# === QUESTIONS - 50 سؤال (5 لكل مستوى) عن BSF وفلسطين وعام ===
# ملاحظة: هذه هي القائمة الكاملة 50 سؤال - انسخها كما هي
QUESTIONS = [
    # المستوى 0 - ملح (5 أسئلة)
    {"level": 0, "category": "BSF", "question": "ما معنى اختصار BSF؟", "options": ["Best Spice Family", "Be Safe Friends", "مبادرة شبابية فلسطينية للبهارات والمعرفة", "Be Strong Forever"], "answer": 2, "explanation": "BSF مبادرة شبابية فلسطينية لنشر المعرفة والثقافة بطريقة ممتعة"},
    {"level": 0, "category": "فلسطين", "question": "ما عاصمة دولة فلسطين؟", "options": ["غزة", "القدس", "رام الله", "نابلس"], "answer": 1, "explanation": "القدس عاصمة فلسطين الأبدية"},
    {"level": 0, "category": "عام", "question": "كم عدد أركان الإسلام؟", "options": ["4", "5", "6", "7"], "answer": 1, "explanation": "أركان الإسلام خمسة"},
    {"level": 0, "category": "عام", "question": "ما لون الملح الطبيعي؟", "options": ["أبيض", "أسود", "أحمر", "أزرق"], "answer": 0, "explanation": "الملح الطبيعي أبيض اللون"},
    {"level": 0, "category": "فلسطين", "question": "ما البحر الذي يقع غرب فلسطين؟", "options": ["البحر الأحمر", "البحر المتوسط", "بحر العرب", "البحر الميت"], "answer": 1, "explanation": "البحر المتوسط غرب فلسطين"},

    # المستوى 1 - كمون (5 أسئلة)
    {"level": 1, "category": "BSF", "question": "من هو مؤسس فكرة بهارتك يا موشي؟", "options": ["الدودة المرشدة", "موشي", "الملك الدود", "تايغر"], "answer": 1, "explanation": "موشي هو بطل القصة وصاحب البهار النهائي"},
    {"level": 1, "category": "فلسطين", "question": "ما هي المدينة المعروفة بكنافة نابلسية؟", "options": ["الخليل", "نابلس", "جنين", "طولكرم"], "answer": 1, "explanation": "نابلس مشهورة بالكنافة النابلسية"},
    {"level": 1, "category": "عام", "question": "الكمون يستخدم غالباً مع:", "options": ["الحلويات", "الفلافل والحمص", "العصائر", "الشاي فقط"], "answer": 1, "explanation": "الكمون أساسي في الفلافل الفلسطيني"},
    {"level": 1, "category": "فلسطين", "question": "ما هو رمز الصمود الفلسطيني؟", "options": ["الزيتون", "البرتقال", "التفاح", "الموز"], "answer": 0, "explanation": "شجرة الزيتون رمز الصمود والجذور"},
    {"level": 1, "category": "BSF", "question": "كم عدد مستويات لعبة بهارتك؟", "options": ["5", "8", "10", "12"], "answer": 2, "explanation": "10 مستويات من ملح إلى بهارتك يا موشي"},

    # المستوى 2 - فلفل (5 أسئلة)
    {"level": 2, "category": "فلسطين", "question": "أين يقع المسجد الأقصى؟", "options": ["غزة", "القدس", "بيت لحم", "أريحا"], "answer": 1, "explanation": "المسجد الأقصى في القدس الشريف"},
    {"level": 2, "category": "عام", "question": "الفلفل الحار يحتوي على مادة:", "options": ["كابسيسين", "كافيين", "نيكوتين", "جلوكوز"], "answer": 0, "explanation": "الكابسيسين هي المادة الحارة"},
    {"level": 2, "category": "BSF", "question": "ما هو حيوان المرشد في اللعبة؟", "options": ["أسد", "نمر", "دودة", "صقر"], "answer": 2, "explanation": "الدودة المرشدة هي دليل اللاعبين الجدد"},
    {"level": 2, "category": "فلسطين", "question": "مدينة يافا مشهورة بـ:", "options": ["البرتقال", "الزيتون", "العنب", "التين"], "answer": 0, "explanation": "برتقال يافا عالمي"},
    {"level": 2, "category": "عام", "question": "كم عدد ألوان قوس قزح؟", "options": ["5", "6", "7", "8"], "answer": 2, "explanation": "7 ألوان"},

    # المستوى 3 - كزبرة (5 أسئلة)
    {"level": 3, "category": "فلسطين", "question": "ما هي عملة فلسطين التاريخية؟", "options": ["الدينار", "الجنيه الفلسطيني", "الشيكل", "الليرة"], "answer": 1, "explanation": "الجنيه الفلسطيني كان العملة قبل 1948"},
    {"level": 3, "category": "BSF", "question": "كم عدد الصناديق في خريطة الكنز؟", "options": ["2", "3", "4", "5"], "answer": 1, "explanation": "3 صناديق كنز في الخريطة 7x7"},
    {"level": 3, "category": "عام", "question": "الكزبرة تنتمي لعائلة:", "options": ["البقوليات", "الخيميات", "النعناع", "الورد"], "answer": 1, "explanation": "الخيميات"},
    {"level": 3, "category": "فلسطين", "question": "ما أقدم مدينة في فلسطين؟", "options": ["القدس", "أريحا", "غزة", "الخليل"], "answer": 1, "explanation": "أريحا أقدم مدينة مأهولة في العالم"},
    {"level": 3, "category": "فلسطين", "question": "المسافة بين الضفة وغزة تقريباً:", "options": ["10 كم", "40 كم", "100 كم", "200 كم"], "answer": 1, "explanation": "حوالي 40 كم"},

    # المستوى 4 - زعتر (5 أسئلة)
    {"level": 4, "category": "فلسطين", "question": "الزعتر الفلسطيني يخلط مع:", "options": ["سكر", "سمسم وسماق", "ملح فقط", "فلفل"], "answer": 1, "explanation": "خلطة الزعتر الفلسطيني الأصلية سمسم وسماق"},
    {"level": 4, "category": "BSF", "question": "ما هو حجم خريطة الكنز؟", "options": ["5x5", "6x6", "7x7", "8x8"], "answer": 2, "explanation": "7x7 مربعات"},
    {"level": 4, "category": "فلسطين", "question": "كنيسة المهد موجودة في:", "options": ["القدس", "بيت لحم", "الناصرة", "أريحا"], "answer": 1, "explanation": "بيت لحم"},
    {"level": 4, "category": "عام", "question": "الزعتر مفيد لـ:", "options": ["المناعة", "النوم فقط", "الطول", "لاشيء"], "answer": 0, "explanation": "يقوي المناعة"},
    {"level": 4, "category": "BSF", "question": "كم وحش في خريطة الكنز؟", "options": ["2", "3", "4", "6"], "answer": 2, "explanation": "4 وحوش تتحرك بنظام مطاردة"},

    # المستوى 5 - قرفة (5 أسئلة)
    {"level": 5, "category": "فلسطين", "question": "قصر هشام موجود في:", "options": ["القدس", "أريحا", "غزة", "نابلس"], "answer": 1, "explanation": "قصر هشام الأموي في أريحا"},
    {"level": 5, "category": "عام", "question": "القرفة أصلها من:", "options": ["سريلانكا", "فلسطين", "مصر", "المغرب"], "answer": 0, "explanation": "سريلانكا أصل القرفة السيلانية"},
    {"level": 5, "category": "BSF", "question": "ما اسم شجرة قصر هشام المشهورة؟", "options": ["شجرة الحياة", "شجرة الزيتون", "شجرة التين", "شجرة الصبر"], "answer": 0, "explanation": "فسيفساء شجرة الحياة في قصر هشام"},
    {"level": 5, "category": "فلسطين", "question": "متى بني قصر هشام؟", "options": ["العصر الأموي", "العصر العباسي", "العصر العثماني", "الروماني"], "answer": 0, "explanation": "العصر الأموي 8م"},
    {"level": 5, "category": "BSF", "question": "كم HP للشخصيات؟", "options": ["50", "100", "150", "يختلف حسب الشخصية"], "answer": 3, "explanation": "كل شخصية لها HP وقوة مختلفة"},

    # المستوى 6 - هيل (5 أسئلة)
    {"level": 6, "category": "عام", "question": "الهيل يسمى ملك:", "options": ["البهارات", "التوابل الحلوة", "القهوة", "الشاي"], "answer": 0, "explanation": "ملكة البهارات"},
    {"level": 6, "category": "فلسطين", "question": "القهوة العربية الفلسطينية تقدم مع:", "options": ["حليب", "تمر", "سكر كثير", "ثلج"], "answer": 1, "explanation": "القهوة مع التمر عادة أصيلة"},
    {"level": 6, "category": "BSF", "question": "كيف تتحرك الوحوش؟", "options": ["عشوائي فقط", "مطاردة إذا المسافة <=3 وإلا عشوائي", "ثابتة", "تطير"], "answer": 1, "explanation": "ذكاء اصطناعي بسيط - مطاردة قريبة"},
    {"level": 6, "category": "فلسطين", "question": "ما هو طبق فلسطين الوطني؟", "options": ["الكبسة", "المسخن", "المنسف", "المقلوبة"], "answer": 1, "explanation": "المسخن طبق وطني فلسطيني"},
    {"level": 6, "category": "عام", "question": "كم عدد حروف اللغة العربية؟", "options": ["26", "28", "29", "32"], "answer": 1, "explanation": "28 حرف"},

    # المستوى 7 - قرنفل (5 أسئلة)
    {"level": 7, "category": "BSF", "question": "ما هو صوت فتح الصندوق؟", "options": ["coin", "box_open", "victory", "move"], "answer": 1, "explanation": "box_open من قاموس SOUNDS"},
    {"level": 7, "category": "فلسطين", "question": "مدينة الخليل مشهورة بصناعة:", "options": ["الزجاج والخزف", "السيارات", "الحديد", "البلاستيك"], "answer": 0, "explanation": "زجاج وخزف الخليل"},
    {"level": 7, "category": "عام", "question": "القرنفل يستخدم كـ:", "options": ["مخدر موضعي طبيعي", "سم", "وقود", "صبغة فقط"], "answer": 0, "explanation": "مخدر طبيعي للأسنان"},
    {"level": 7, "category": "فلسطين", "question": "ما هو أخفض مكان في العالم؟", "options": ["البحر الميت", "وادي الأردن", "صحراء النقب", "جبل الشيخ"], "answer": 0, "explanation": "البحر الميت -430م"},
    {"level": 7, "category": "BSF", "question": "ما عقوبة لمس الوحش؟", "options": ["لا شيء", "نقص HP", "طرد", "إعادة من البداية"], "answer": 1, "explanation": "الوحش ينقص HP"},

    # المستوى 8 - زعفران (5 أسئلة)
    {"level": 8, "category": "عام", "question": "الزعفران أغلى بهار لأنه:", "options": ["نادر ويحتاج 150 زهرة لغرام واحد", "مستورد من المريخ", "سام", "يصنع من ذهب"], "answer": 0, "explanation": "150 زهرة = 1غ"},
    {"level": 8, "category": "فلسطين", "question": "كم عدد محافظات فلسطين؟", "options": ["10", "12", "16", "20"], "answer": 2, "explanation": "16 محافظة"},
    {"level": 8, "category": "BSF", "question": "كيف تتحرك العوائق؟", "options": ["ثابتة", "أفقي/عمودي وتنعكس عند الجدار", "دائرية", "عشوائية"], "answer": 1, "explanation": "flip at walls"},
    {"level": 8, "category": "فلسطين", "question": "ما معنى كلمة فلسطين؟", "options": ["أرض الكنعانيين", "أرض الزيتون", "أسماء مختلفة - بلست"], "answer": 2, "explanation": "من الشعوب الفلسطينية بلست"},
    {"level": 8, "category": "عام", "question": "ما أطول نهر في العالم؟", "options": ["النيل", "الأمازون", "المسيسيبي", "الفرات"], "answer": 0, "explanation": "النيل"},

    # المستوى 9 - بهارتك يا موشي (5 أسئلة نهائية صعبة)
    {"level": 9, "category": "BSF", "question": "ما هي جائزة بهارتك يا موشي النهائية؟", "options": ["10", "100", "1000 نقطة + لقب أسطورة", "لا شيء"], "answer": 2, "explanation": "1000 نقطة ولقب أسطورة البهارات"},
    {"level": 9, "category": "فلسطين", "question": "قصر هشام يحتوي على أكبر أرضية فسيفساء في:", "options": ["العالم", "الشرق الأوسط", "فلسطين", "أريحا"], "answer": 0, "explanation": "أكبر أرضية فسيفساء متصلة في العالم"},
    {"level": 9, "category": "BSF", "question": "ما هو دور KING_WORM؟", "options": ["عدو", "يعطي التاج النهائي بعد فتح 3 صناديق", "يبيع بهارات", "لا دور"], "answer": 1, "explanation": "الملك الدود حارس التاج"},
    {"level": 9, "category": "فلسطين", "question": "فسيفساء شجرة الحياة ترمز لـ:", "options": ["الحرب والسلام", "الصراع بين الخير والشر", "الزراعة", "الماء"], "answer": 1, "explanation": "أسد يهاجم غزالين - رمز الصراع الأبدي"},
    {"level": 9, "category": "عام", "question": "ما هي البهارات السبع؟", "options": ["خلطة سرية كل عائلة مختلفة", "7 أنواع ثابتة عالمياً", "ملح وفلفل فقط", "لا وجود لها"], "answer": 0, "explanation": "تختلف من عائلة لعائلة - سر العائلة"},
]

# === دوال البيانات ===

def load_user_data() -> Dict:
    """تحميل بيانات المستخدمين من ملف أو Redis"""
    if redis_client:
        # سيتم التحميل async في الـ cog لذا نرجع dict فارغ هنا للتهيئة
        return {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_user_data(data: Dict):
    """حفظ البيانات - متزامن للملف، وغير متزامن لـ Redis يتم في الـ cog"""
    if not redis_client:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[BSF] خطأ حفظ: {e}")

async def save_user_data_async(data: Dict):
    """نسخة async مع دعم Redis"""
    if redis_client:
        try:
            await redis_client.set(REDIS_KEY, json.dumps(data, ensure_ascii=False))
            return
        except Exception as e:
            print(f"[BSF Redis] خطأ: {e}")
    save_user_data(data)

async def load_user_data_async() -> Dict:
    """نسخة async"""
    if redis_client:
        try:
            raw = await redis_client.get(REDIS_KEY)
            if raw:
                return json.loads(raw)
        except Exception as e:
            print(f"[BSF Redis] خطأ تحميل: {e}")
    return load_user_data()

def get_unseen_question(user_data: Dict, user_id: str, level: int) -> Optional[Dict]:
    """إرجاع سؤال لم يره المستخدم في هذا المستوى"""
    seen = user_data.get(user_id, {}).get("seen_questions", [])
    pool = [q for q in QUESTIONS if q["level"] == level and QUESTIONS.index(q) not in seen]
    if not pool:
        # إذا شاهد كل الأسئلة، أعد التدوير
        pool = [q for q in QUESTIONS if q["level"] == level]
    return random.choice(pool) if pool else None

def render_map(player_pos: Tuple[int,int], opened_boxes: List[int], visited: List[Tuple[int,int]], moving_obstacles=None, moving_monsters=None) -> str:
    """رسم الخريطة 7x7 بالإيموجي - نصي للـ Discord"""
    # 0=فارغ 1=جدار 2=عائق متحرك (يتم حسابه خارجياً)
    grid = [row[:] for row in MAP_TEMPLATE]
    rows = []
    for y in range(7):
        line = ""
        for x in range(7):
            pos = (x, y)
            if pos == player_pos:
                line += "🧑‍🌾"
            elif moving_monsters and pos in [m["pos"] for m in moving_monsters]:
                line += "👹"
            elif moving_obstacles and pos in [o["pos"] for o in moving_obstacles]:
                line += "🪨"
            elif pos in [TREASURE_BOXES[i]["pos"] for i in range(len(TREASURE_BOXES)) if i not in opened_boxes]:
                line += "📦"
            elif pos in [TREASURE_BOXES[i]["pos"] for i in range(len(TREASURE_BOXES)) if i in opened_boxes]:
                line += "✅"
            elif pos in visited:
                line += "· "
            elif grid[y][x] == 1:
                line += "🧱"
            else:
                line += "⬜"
        rows.append(line)
    return "\n".join(rows)

# === HISHAM_PUZZLES - 4 ألغاز عن قصر هشام ===
HISHAM_PUZZLES = [
    {
        "id": 0,
        "title": "عصر قصر هشام",
        "question": "في أي عصر بني قصر هشام في أريحا؟",
        "options": ["الأموي", "العباسي", "الفاطمي", "العثماني"],
        "answer": 0,
        "hint": "بناه هشام بن عبد الملك",
        "reward": 50,
        "image_desc": "قصر صحراوي أموي"
    },
    {
        "id": 1,
        "title": "شجرة الحياة",
        "question": "ماذا تصور فسيفساء شجرة الحياة الشهيرة؟",
        "options": ["أسد يهاجم غزالين تحت شجرة", "نخلة وبحر", "زهرة لوتس", "خريطة فلسطين"],
        "answer": 0,
        "hint": "رمز الصراع بين القوة والضعف",
        "reward": 75,
        "image_desc": "فسيفساء ملونة لشجرة"
    },
    {
        "id": 2,
        "title": "موقع القصر",
        "question": "أين يقع قصر هشام تحديداً؟",
        "options": ["شمال أريحا - خربة المفجر", "وسط القدس", "جنوب الخليل", "غرب غزة"],
        "answer": 0,
        "hint": "خربة المفجر",
        "reward": 60,
        "image_desc": "أطلال قصر في الصحراء"
    },
    {
        "id": 3,
        "title": "قطع الفسيفساء",
        "question": "كم عدد قطع الفسيفساء التقريبي في أرضية قصر هشام؟",
        "options": ["5 مليون", "21 مليون", "38 مليون", "100 مليون"],
        "answer": 2,
        "hint": "أكبر أرضية فسيفساء متصلة في العالم",
        "reward": 100,
        "image_desc": "أرضية فسيفساء ضخمة"
    },
]

# === PLAYABLE_CHARACTERS - 6 شخصيات ===
PLAYABLE_CHARACTERS = [
    {"id": "tiger_explorer", "name": "نمر المستكشف", "emoji": "🐯", "power": 15, "hp": 120, "speed": 2, "desc": "سريع وقوي - يكسر الحواجز", "ability": "قفزة النمر"},
    {"id": "lion_explorer", "name": "أسد البادية", "emoji": "🦁", "power": 18, "hp": 140, "speed": 1, "desc": "ملك الصحراء - يخيف الوحوش", "ability": "زئير مرعب"},
    {"id": "mousa_explorer", "name": "موشي الأسطورة", "emoji": "👨‍🍳", "power": 20, "hp": 100, "speed": 3, "desc": "صاحب البهار النهائي - حظ مضاعف", "ability": "بهارتك يا موشي!"},
    {"id": "worm_explorer", "name": "دودة الحكمة", "emoji": "🪱", "power": 10, "hp": 80, "speed": 4, "desc": "صغيرة وسريعة - تمر من الشقوق", "ability": "تلميح مجاني"},
    {"id": "tiger_hoodie", "name": "تايغر هودي", "emoji": "🐅", "power": 16, "hp": 110, "speed": 2, "desc": "ستايل الشارع - يتفادى الوحوش", "ability": "اختفاء"},
    {"id": "lion_hoodie", "name": "لايون هودي", "emoji": "🦁‍🎤", "power": 17, "hp": 130, "speed": 2, "desc": "هيبة وهدوء - مقاوم للعوائق", "ability": "درع ترابي"},
]

# === كائنات اللعبة ===
GUIDE_WORM = {"name": "الدودة المرشدة", "emoji": "🪱✨", "role": "مرشد المبتدئين", "dialogue": "أهلاً يا بطل! اتبعني للكنز، لكن احذر الوحوش!"}
KING_WORM = {"name": "الملك الدود", "emoji": "👑🪱", "role": "حارس التاج", "dialogue": "أحسنت! فتحت كل الصناديق، الآن خذ تاج بهارتك يا موشي!"}

MAP_TEMPLATE = [
    [0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
]

TREASURE_BOXES = [
    {"id": 0, "pos": (6, 0), "prize": 100, "emoji": "📦", "content": "بهارات نادرة"},
    {"id": 1, "pos": (0, 6), "prize": 150, "emoji": "🎁", "content": "وصفة سرية"},
    {"id": 2, "pos": (6, 6), "prize": 300, "emoji": "👑", "content": "تاج موشي"},
]

MONSTERS = [
    {"id": 0, "name": "وحش الملح", "emoji": "👹", "pos": (2, 1), "hp": 30, "damage": 10, "move_type": "horizontal"},
    {"id": 1, "name": "دودة الظلام", "emoji": "🐛", "pos": (4, 3), "hp": 20, "damage": 15, "move_type": "vertical"},
    {"id": 2, "name": "حارس القصر", "emoji": "👺", "pos": (1, 4), "hp": 40, "damage": 20, "move_type": "chase"},
    {"id": 3, "name": "عفريت الرمل", "emoji": "👻", "pos": (5, 2), "hp": 25, "damage": 12, "move_type": "random"},
]

SOUNDS = {
    "move": "🔊 *تيك* - خطوة",
    "obstacle": "💥 *دوم* - اصطدمت بحاجز متحرك!",
    "monster": "😱 *غغغرر* - وحش!",
    "box_open": "🎉 *تششش* - فتحت الصندوق!",
    "coin": "🪙 *رنين* - كسبت نقاط!",
    "victory": "🏆 *تهليل* - انتصار!",
    "hisham": "🏛️ *صدى تاريخي* - قصر هشام",
    "wrong": "❌ *بوف* - إجابة خاطئة",
    "correct": "✅ *دينغ* - إجابة صحيحة!",
}

# === QuizView - واجهة أسئلة البهارات ===
class QuizView(discord.ui.View):
    def __init__(self, question: Dict, user_id: str, level: int, bot_data: Dict):
        super().__init__(timeout=60)
        self.question = question
        self.user_id = user_id
        self.level = level
        self.bot_data = bot_data
        # إنشاء أزرار الاختيارات
        for idx, opt in enumerate(question["options"]):
            btn = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.secondary, custom_id=f"opt_{idx}")
            btn.callback = self.make_callback(idx)
            self.add_item(btn)

    def make_callback(self, idx: int):
        async def callback(interaction: discord.Interaction):
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("❌ ليس دورك!", ephemeral=True)
                return
            is_correct = (idx == self.question["answer"])
            user = self.bot_data.setdefault(self.user_id, {"points":0, "level":0, "seen_questions":[], "hisham_solved":[], "treasure":{}})
            q_index = QUESTIONS.index(self.question)
            if q_index not in user["seen_questions"]:
                user["seen_questions"].append(q_index)

            if is_correct:
                prize = BAHARAT_LEVELS[self.level]["prize"]
                user["points"] += prize
                if self.level >= user["level"]:
                    user["level"] = min(self.level+1, 9)
                await save_user_data_async(self.bot_data)
                embed = discord.Embed(title=f"{SOUNDS['correct']} {BAHARAT_LEVELS[self.level]['emoji']} إجابة صحيحة!", description=f"{self.question['explanation']}\n\n💰 ربحت {prize} نقطة!\n{SOUNDS['coin']}", color=0x2ECC71)
                view = NextQuestionView(self.user_id, self.level, self.bot_data)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = discord.Embed(title=f"{SOUNDS['wrong']} إجابة خاطئة", description=f"الصحيح: **{self.question['options'][self.question['answer']]}**\n{self.question['explanation']}", color=0xE74C3C)
                view = NextQuestionView(self.user_id, self.level, self.bot_data, retry=True)
                await interaction.response.edit_message(embed=embed, view=view)
            self.stop()
        return callback

class NextQuestionView(discord.ui.View):
    def __init__(self, user_id: str, level: int, bot_data: Dict, retry=False):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.level = level
        self.bot_data = bot_data
        self.retry = retry

    @discord.ui.button(label="➡️ السؤال التالي", style=discord.ButtonStyle.primary)
    async def next_q(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ ليس لك!", ephemeral=True)
            return
        q = get_unseen_question(self.bot_data, self.user_id, self.level)
        if not q:
            await interaction.response.send_message("🎉 أنهيت كل أسئلة هذا المستوى! استخدم /بهاراتك للانتقال للمستوى التالي", ephemeral=True)
            return
        embed = discord.Embed(title=f"{BAHARAT_LEVELS[q['level']]['emoji']} {BAHARAT_LEVELS[q['level']]['name']} - {q['category']}", description=f"**{q['question']}**", color=BAHARAT_LEVELS[q['level']]['color'])
        view = QuizView(q, self.user_id, q["level"], self.bot_data)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🏠 القائمة", style=discord.ButtonStyle.secondary)
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = self.bot_data.get(self.user_id, {"points":0, "level":0})
        embed = discord.Embed(title="📜 قائمة بهارتك", description=f"مستواك: {BAHARAT_LEVELS[user['level']]['emoji']} {BAHARAT_LEVELS[user['level']]['name']}\nنقاطك: {user['points']}", color=0xFF6B2D)
        await interaction.response.edit_message(embed=embed, view=None)

# === BaharatGame Cog ===
class BaharatGame(commands.Cog):
    """كوج بهارتك - 10 مستويات"""
    def __init__(self, bot):
        self.bot = bot
        self.data = load_user_data()

    async def cog_load(self):
        self.data = await load_user_data_async()

    @app_commands.command(name="بهاراتك", description="ابدأ رحلة البهارات العشرة من ملح إلى بهارتك يا موشي")
    async def baharatak(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.data = await load_user_data_async()
        user_id = str(interaction.user.id)
        user = self.data.get(user_id, {"points":0, "level":0, "seen_questions":[]})
        level = user["level"]
        level_info = BAHARAT_LEVELS[level]
        q = get_unseen_question(self.data, user_id, level)
        if not q:
            q = random.choice([qq for qq in QUESTIONS if qq["level"]==level])
        embed = discord.Embed(
            title=f"{level_info['emoji']} مستوى {level_info['name']} - {level_info['desc']}",
            description=f"**{q['question']}**\n\n💰 الجائزة: {level_info['prize']} نقطة\n{GUIDE_WORM['emoji']} {GUIDE_WORM['dialogue']}",
            color=level_info["color"]
        )
        embed.set_footer(text=f"التصنيف: {q['category']} | المستوى {level+1}/10")
        view = QuizView(q, user_id, q["level"], self.data)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="رصيدي", description="اعرض رصيدك وتقدمك في بهارتك")
    async def raseedi(self, interaction: discord.Interaction):
        self.data = await load_user_data_async()
        user_id = str(interaction.user.id)
        user = self.data.get(user_id)
        if not user:
            await interaction.response.send_message("❌ لم تبدأ بعد! استخدم /بهاراتك", ephemeral=True)
            return
        level_info = BAHARAT_LEVELS[user["level"]]
        embed = discord.Embed(title=f"💼 رصيد {interaction.user.display_name}", color=level_info["color"])
        embed.add_field(name="المستوى الحالي", value=f"{level_info['emoji']} {level_info['name']}", inline=True)
        embed.add_field(name="النقاط", value=f"{user['points']} 🪙", inline=True)
        embed.add_field(name="أسئلة مجابة", value=f"{len(user.get('seen_questions',[]))}/50", inline=True)
        embed.add_field(name="قصر هشام", value=f"{len(user.get('hisham_solved',[]))}/4 ألغاز", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="توب_بهارات", description="لوحة صدارة بهارتك")
    async def top_baharat(self, interaction: discord.Interaction):
        self.data = await load_user_data_async()
        sorted_users = sorted(self.data.items(), key=lambda x: x[1].get("points",0), reverse=True)[:10]
        desc = ""
        for i, (uid, udata) in enumerate(sorted_users, 1):
            lvl = BAHARAT_LEVELS[udata.get("level",0)]
            medal = ["🥇","🥈","🥉"][i-1] if i<=3 else f"{i}."
            desc += f"{medal} <@{uid}> - {lvl['emoji']} {lvl['name']} - {udata.get('points',0)} نقطة\n"
        embed = discord.Embed(title="🏆 توب بهارات - لوحة الصدارة", description=desc or "لا يوجد لاعبين بعد", color=0xFFD700)
        await interaction.response.send_message(embed=embed)

# === Hisham Palace Views ===
class HishamAnswerButton(discord.ui.Button):
    def __init__(self, idx: int, label: str, is_correct: bool, puzzle: Dict, user_id: str, bot_data: Dict):
        super().__init__(label=label[:80], style=discord.ButtonStyle.secondary)
        self.idx = idx
        self.is_correct = is_correct
        self.puzzle = puzzle
        self.user_id = user_id
        self.bot_data = bot_data

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ ليس لك!", ephemeral=True)
            return
        user = self.bot_data.setdefault(self.user_id, {"points":0, "level":0, "seen_questions":[], "hisham_solved":[], "treasure":{}})
        if self.is_correct:
            if self.puzzle["id"] not in user["hisham_solved"]:
                user["hisham_solved"].append(self.puzzle["id"])
                user["points"] += self.puzzle["reward"]
                await save_user_data_async(self.bot_data)
            embed = discord.Embed(title=f"{SOUNDS['hisham']} {SOUNDS['correct']}", description=f"أحسنت! {self.puzzle['title']}\n💰 +{self.puzzle['reward']} نقطة\n\n{self.puzzle['hint']}", color=0x2ECC71)
            view = HishamQuizView(self.user_id, self.bot_data, solved=self.puzzle["id"])
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            embed = discord.Embed(title=SOUNDS["wrong"], description=f"خطأ! الصحيح: **{self.puzzle['options'][self.puzzle['answer']]}**", color=0xE74C3C)
            await interaction.response.edit_message(embed=embed, view=self.view)

class HishamQuizView(discord.ui.View):
    def __init__(self, user_id: str, bot_data: Dict, solved=None):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bot_data = bot_data
        # اختيار لغز لم يحل
        user = bot_data.get(user_id, {"hisham_solved":[]})
        unsolved = [p for p in HISHAM_PUZZLES if p["id"] not in user.get("hisham_solved",[])]
        if not unsolved:
            return
        puzzle = random.choice(unsolved)
        self.puzzle = puzzle
        for idx, opt in enumerate(puzzle["options"]):
            is_corr = (idx == puzzle["answer"])
            self.add_item(HishamAnswerButton(idx, opt, is_corr, puzzle, user_id, bot_data))

class HishamPalaceView(discord.ui.View):
    def __init__(self, user_id: str, bot_data: Dict):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bot_data = bot_data

    @discord.ui.button(label="🏛️ ابدأ لغز قصر هشام", style=discord.ButtonStyle.primary, emoji="🏛️")
    async def start_puzzle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ ليس لك!", ephemeral=True)
            return
        user = self.bot_data.get(self.user_id, {"hisham_solved":[]})
        unsolved = [p for p in HISHAM_PUZZLES if p["id"] not in user.get("hisham_solved",[])]
        if not unsolved:
            embed = discord.Embed(title="🎉 أنهيت كل ألغاز قصر هشام!", description=f"{SOUNDS['victory']} أنت خبير تاريخي!\n\nمجموع الألغاز: 4/4", color=0xFFD700)
            await interaction.response.edit_message(embed=embed, view=None)
            return
        puzzle = random.choice(unsolved)
        embed = discord.Embed(title=f"🏛️ {puzzle['title']}", description=f"**{puzzle['question']}**\n\n💡 تلميح: {puzzle['hint']}\n💰 الجائزة: {puzzle['reward']}", color=0x8B4513)
        view = HishamQuizView(self.user_id, self.bot_data)
        view.puzzle = puzzle
        # إعادة بناء الأزرار للغز المختار
        view.clear_items()
        for idx, opt in enumerate(puzzle["options"]):
            view.add_item(HishamAnswerButton(idx, opt, idx==puzzle["answer"], puzzle, self.user_id, self.bot_data))
        await interaction.response.edit_message(embed=embed, view=view)

class HishamPalace(commands.Cog):
    """كوج قصر هشام - 4 ألغاز تاريخية"""
    def __init__(self, bot):
        self.bot = bot
        self.data = {}

    async def cog_load(self):
        self.data = await load_user_data_async()

    @app_commands.command(name="قصر_هشام", description="استكشف ألغاز قصر هشام الأموي في أريحا")
    async def qasr_hisham(self, interaction: discord.Interaction):
        self.data = await load_user_data_async()
        user_id = str(interaction.user.id)
        user = self.data.get(user_id, {"hisham_solved":[]})
        solved = len(user.get("hisham_solved",[]))
        embed = discord.Embed(
            title="🏛️ قصر هشام - خربة المفجر",
            description=f"{SOUNDS['hisham']}\n\nقصر أموي بناه هشام بن عبد الملك (724-743م)\nيضم أكبر أرضية فسيفساء متصلة في العالم!\n\n**شجرة الحياة**: فسيفساء أسد يهاجم غزالين تحت شجرة\n\n📊 تقدمك: {solved}/4 ألغاز\n{GUIDE_WORM['emoji']} {GUIDE_WORM['dialogue']}",
            color=0x8B4513
        )
        embed.set_footer(text="أريحا - أقدم مدينة في العالم")
        view = HishamPalaceView(user_id, self.data)
        await interaction.response.send_message(embed=embed, view=view)

# === Character Select & GameView مع move_entities ===
class CharacterButton(discord.ui.Button):
    def __init__(self, char: Dict):
        super().__init__(label=f"{char['emoji']} {char['name']}", style=discord.ButtonStyle.secondary)
        self.char = char

    async def callback(self, interaction: discord.Interaction):
        # بدء اللعبة بهذه الشخصية
        view = GameView(interaction.user.id, self.char, interaction.client.baharat_data if hasattr(interaction.client, 'baharat_data') else {})
        embed = view.get_embed()
        await interaction.response.edit_message(embed=embed, view=view)

class CharacterSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for char in PLAYABLE_CHARACTERS:
            self.add_item(CharacterButton(char))

class GameView(discord.ui.View):
    """واجهة لعبة الكنز المتحرك - مع نظام حركة العوائق والوحوش"""
    def __init__(self, user_id: int, character: Dict, bot_data: Dict):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.character = character
        self.bot_data = bot_data
        self.player_pos = (0, 0)
        self.visited = [(0,0)]
        self.opened_boxes = []
        self.hp = character["hp"]
        self.points = 0
        self.moving_obstacles = [
            {"pos": (3, 1), "dir": "h", "dx": 1},
            {"pos": (2, 4), "dir": "v", "dy": 1},
        ]
        self.moving_monsters = [m.copy() for m in MONSTERS]
        self.alert = f"{SOUNDS['move']} بدأت المغامرة بـ {character['emoji']} {character['name']}!"

    def get_embed(self):
        map_str = render_map(self.player_pos, self.opened_boxes, self.visited, self.moving_obstacles, self.moving_monsters)
        embed = discord.Embed(
            title=f"🗺️ كنز البهارات - {self.character['emoji']} {self.character['name']}",
            description=f"```\n{map_str}\n```\n{self.alert}\n\n❤️ HP: {self.hp}/{self.character['hp']} | 🪙 {self.points} | 📦 {len(self.opened_boxes)}/3",
            color=0x2ECC71 if self.hp>50 else 0xE74C3C
        )
        embed.set_footer(text=f"{self.character['ability']} | استخدم الأسهم للحركة")
        return embed

    def move_entities(self):
        """تحريك الكائنات كل دور - عوائق تنعكس عند الجدار، وحوش تطارد إذا المسافة <=3 وإلا عشوائي"""
        # --- تحريك العوائق ---
        for obs in self.moving_obstacles:
            x, y = obs["pos"]
            if obs["dir"] == "h":
                nx = x + obs["dx"]
                # انعكاس عند الجدار أو حدود الخريطة
                if nx < 0 or nx >= 7 or MAP_TEMPLATE[y][nx] == 1:
                    obs["dx"] *= -1
                    nx = x + obs["dx"]
                obs["pos"] = (nx, y)
            else:  # vertical
                ny = y + obs.get("dy", 1)
                if ny < 0 or ny >= 7 or MAP_TEMPLATE[ny][x] == 1:
                    obs["dy"] *= -1
                    ny = y + obs["dy"]
                obs["pos"] = (x, ny)

        # --- تحريك الوحوش ---
        for monster in self.moving_monsters:
            mx, my = monster["pos"]
            px, py = self.player_pos
            distance = abs(mx - px) + abs(my - py)  # Manhattan
            if distance <= 3:
                # مطاردة: تحرك نحو اللاعب
                if mx < px and mx+1 < 7 and MAP_TEMPLATE[my][mx+1] != 1:
                    monster["pos"] = (mx+1, my)
                elif mx > px and mx-1 >=0 and MAP_TEMPLATE[my][mx-1] != 1:
                    monster["pos"] = (mx-1, my)
                elif my < py and my+1 <7 and MAP_TEMPLATE[my+1][mx] != 1:
                    monster["pos"] = (mx, my+1)
                elif my > py and my-1 >=0 and MAP_TEMPLATE[my-1][mx] != 1:
                    monster["pos"] = (mx, my-1)
                monster["alert"] = "👹 يطاردك!"
            else:
                # حركة عشوائية
                dirs = [(0,1),(0,-1),(1,0),(-1,0)]
                random.shuffle(dirs)
                for dx, dy in dirs:
                    nx, ny = mx+dx, my+dy
                    if 0 <= nx <7 and 0 <= ny <7 and MAP_TEMPLATE[ny][nx] != 1:
                        monster["pos"] = (nx, ny)
                        break

    async def handle_move(self, interaction: discord.Interaction, dx: int, dy: int):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ ليس دورك!", ephemeral=True)
            return
        x, y = self.player_pos
        nx, ny = x+dx, y+dy
        # تحقق الحدود والجدران
        if not (0 <= nx <7 and 0 <= ny <7):
            self.alert = f"{SOUNDS['obstacle']} جدار! لا يمكنك الخروج"
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
            return
        if MAP_TEMPLATE[ny][nx] == 1:
            self.alert = f"{SOUNDS['obstacle']} 🧱 جدار صلب!"
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
            return
        # تحريك اللاعب
        self.player_pos = (nx, ny)
        if self.player_pos not in self.visited:
            self.visited.append(self.player_pos)

        # تحريك الكائنات بعد كل حركة لاعب (turn-based)
        self.move_entities()

        # تحقق اصطدام بعائق متحرك
        if self.player_pos in [o["pos"] for o in self.moving_obstacles]:
            self.hp -= 10
            self.alert = f"{SOUNDS['obstacle']} اصطدمت بحجر متحرك! -10 HP"

        # تحقق وحش
        for m in self.moving_monsters:
            if m["pos"] == self.player_pos:
                self.hp -= m["damage"]
                self.alert = f"{SOUNDS['monster']} {m['name']} هاجمك! -{m['damage']} HP"

        # تحقق صندوق
        for box in TREASURE_BOXES:
            if box["pos"] == self.player_pos and box["id"] not in self.opened_boxes:
                self.opened_boxes.append(box["id"])
                self.points += box["prize"]
                self.alert = f"{SOUNDS['box_open']} {SOUNDS['coin']} فتحت {box['content']}! +{box['prize']}"

        # تحقق موت
        if self.hp <= 0:
            embed = discord.Embed(title="💀 انتهت المغامرة!", description=f"{self.alert}\n\nنقاطك: {self.points}\n{GUIDE_WORM['emoji']} حاول مرة أخرى!", color=0xE74C3C)
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
            return

        # تحقق فوز
        if len(self.opened_boxes) == 3:
            embed = discord.Embed(title=f"{SOUNDS['victory']} {KING_WORM['emoji']} انتصار!", description=f"{KING_WORM['dialogue']}\n\n{SOUNDS['coin']} مجموع نقاطك: {self.points+500}\n🏆 حصلت على تاج بهارتك يا موشي!", color=0xFFD700)
            # حفظ النقاط
            if hasattr(self, 'bot_data'):
                user_id_str = str(self.user_id)
                user = self.bot_data.setdefault(user_id_str, {"points":0, "level":0, "seen_questions":[], "hisham_solved":[], "treasure":{}})
                user["points"] += self.points + 500
                await save_user_data_async(self.bot_data)
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
            return

        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.primary, row=0)
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_move(interaction, 0, -1)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.primary, row=1)
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_move(interaction, 0, 1)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, row=1)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_move(interaction, -1, 0)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, row=1)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_move(interaction, 1, 0)

    @discord.ui.button(label="🔍 خريطة", style=discord.ButtonStyle.secondary, row=0)
    async def map_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"```\n{render_map(self.player_pos, self.opened_boxes, self.visited, self.moving_obstacles, self.moving_monsters)}\n```", ephemeral=True)

# === TreasureHunt Cog ===
class TreasureHunt(commands.Cog):
    """كوج الكنز المتحرك"""
    def __init__(self, bot):
        self.bot = bot
        self.data = {}

    async def cog_load(self):
        self.data = await load_user_data_async()
        # حفظ مرجع للوصول من GameView
        self.bot.baharat_data = self.data

    @app_commands.command(name="كنز", description="ابدأ مغامرة الكنز المتحرك 7x7 مع وحوش وعوائق متحركة")
    async def kanz(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🗺️ اختر شخصيتك - مغامرة الكنز",
            description="اختر بطلك وادخل متاهة 7x7 مليئة بالعوائق المتحركة والوحوش المطاردة!\n\n📦 3 صناديق | 👹 4 وحوش | 🪨 عوائق تتحرك كل دور\n\n**نظام الحركة:**\n- العوائق: أفقي/عمودي وتنعكس عند الجدار\n- الوحوش: تطاردك إذا المسافة <=3 وإلا عشوائي\n- Turn-based: تتحرك بعد كل خطوة لك",
            color=0xFF6B2D
        )
        for char in PLAYABLE_CHARACTERS:
            embed.add_field(name=f"{char['emoji']} {char['name']}", value=f"HP:{char['hp']} | قوة:{char['power']} | {char['ability']}", inline=True)
        view = CharacterSelectView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="خريطة_الدود", description="اعرض خريطة الكنز الحالية ونصائح الدودة المرشدة")
    async def kharita_dood(self, interaction: discord.Interaction):
        map_str = render_map((0,0), [], [(0,0)])
        embed = discord.Embed(
            title=f"{GUIDE_WORM['emoji']} خريطة الدودة المرشدة",
            description=f"```\n{map_str}\n```\n{GUIDE_WORM['dialogue']}\n\n**رموز الخريطة:**\n🧑‍🌾 أنت | 📦 صندوق | 🧱 جدار | 🪨 عائق متحرك | 👹 وحش | ⬜ فارغ",
            color=0x9C27B0
        )
        await interaction.response.send_message(embed=embed)

# === SoundsCog ===
class SoundsCog(commands.Cog):
    """كوج الأصوات"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="اصوات", description="استمع لأصوات اللعبة - move, obstacle, monster, box_open, coin, victory, hisham, wrong, correct")
    async def aswat(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔊 مكتبة أصوات BSF Bot", description="الأصوات المستخدمة في اللعبة (نصية للـ Discord):", color=0x00BCD4)
        for key, val in SOUNDS.items():
            embed.add_field(name=key, value=val, inline=True)
        embed.set_footer(text="الأصوات تظهر كرسائل مع كل حدث")
        await interaction.response.send_message(embed=embed)

# === الإعداد النهائي - تحميل كل الـ Cogs الأربعة ===
async def setup(bot: commands.Bot):
    """تحميل كل الكوجز - النسخة المدمجة النهائية"""
    await bot.add_cog(BaharatGame(bot))
    await bot.add_cog(HishamPalace(bot))
    await bot.add_cog(TreasureHunt(bot))
    await bot.add_cog(SoundsCog(bot))
    print("[BSF] ✅ تم تحميل 4 كوجز: BaharatGame, HishamPalace, TreasureHunt, SoundsCog")
    print(f"[BSF] 📦 الأسئلة: {len(QUESTIONS)} | 🎭 الشخصيات: {len(PLAYABLE_CHARACTERS)} | 🏛️ ألغاز قصر هشام: {len(HISHAM_PUZZLES)}")
