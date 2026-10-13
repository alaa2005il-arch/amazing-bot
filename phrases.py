"""
BSF Bot - Professional Edition v2.5.0
Author: BSF Team - Senior Discord Bot Architect
Version: 2.5.0 | Moving Obstacles & Playable Abilities Update
Description: Advanced Discord bot with 4 integrated games, moving obstacles, chasing monsters AI, playable abilities, Hisham Palace historical quest
License: MIT
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

import discord
from discord import app_commands
from discord.ext import commands, tasks

# Optional Redis - graceful fallback
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# ─────────────────────────────────────────────
# Logging Configuration - احترافي
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BSF.BaharatPro")

# ─────────────────────────────────────────────
# Enums & Dataclasses - Typing First
# ─────────────────────────────────────────────
class GameState(Enum):
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class AbilityType(Enum):
    JUMP = "jump"
    ROAR = "roar"
    HINT = "hint"
    RADAR = "radar"
    DASH = "dash"
    SHIELD = "shield"

@dataclass
class Position:
    """Represents a 2D position on the map."""
    x: int
    y: int

    def __add__(self, other: Tuple[int, int]) -> "Position":
        dx, dy = other
        return Position(self.x + dx, self.y + dy)

    def distance_to(self, other: "Position") -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)

@dataclass
class PlayerSession:
    user_id: int
    guild_id: int
    character_id: str
    pos: Position
    level: int = 1
    xp: int = 0
    health: int = 100
    score: int = 0
    shield_active: bool = False
    shield_expires: float = 0.0
    ability_cooldowns: Dict[str, float] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    current_riddle: Optional[str] = None
    moves_count: int = 0

@dataclass
class ObstacleState:
    pos: Position
    direction: Direction
    symbol: str = "🪨"
    movable: bool = True
    last_move: float = 0.0

@dataclass
class MonsterState:
    id: str
    pos: Position
    monster_type: str
    chase_range: int = 5
    damage: int = 20
    scared_until: float = 0.0
    emoji: str = "👾"

@dataclass
class TreasureBox:
    id: str
    pos: Position
    riddle: str
    answer: str
    reward_xp: int
    reward_item: str
    is_opened: bool = False

# ─────────────────────────────────────────────
# Constants - ثوابت احترافية UPPER_CASE
# ─────────────────────────────────────────────
MAP_WIDTH = 11
MAP_HEIGHT = 11
MAX_HEALTH = 100
MOVE_COOLDOWN_SEC = 0.8
ABILITY_ICONS: Dict[str, str] = {
    "jump": "🦘",
    "roar": "🗣️",
    "hint": "💡",
    "radar": "📡",
    "dash": "💨",
    "shield": "🛡️",
}

BAHARAT_LEVELS: List[Dict[str, Any]] = [
    {"id": 1, "name": "مبتدئ البهارات", "name_en": "Spice Novice", "xp_required": 0, "color": 0x9CA3AF, "emoji": "🌿"},
    {"id": 2, "name": "تاجر التوابل", "name_en": "Spice Trader", "xp_required": 250, "color": 0xF59E0B, "emoji": "🧂"},
    {"id": 3, "name": "خبير البهارات", "name_en": "Spice Expert", "xp_required": 750, "color": 0xEF4444, "emoji": "🔥"},
    {"id": 4, "name": "ماستر البهارات", "name_en": "Spice Master", "xp_required": 1500, "color": 0x8B5CF6, "emoji": "👑"},
    {"id": 5, "name": "أسطورة البهارات", "name_en": "Legend", "xp_required": 3000, "color": 0xFBBF24, "emoji": "⚜️"},
]

# 50 سؤال احترافي - بهارات + ثقافة + تاريخ
QUESTIONS: List[Dict[str, Any]] = [
    {"id": 1, "question": "ما هو الموطن الأصلي للفلفل الأسود؟", "options": ["الهند - ساحل مالابار", "المكسيك", "إثيوبيا", "اليمن"], "answer": 0, "level": 1, "spice": "فلفل أسود", "hint": "يُلقب بملك البهارات وبدأ من جنوب الهند"},
    {"id": 2, "question": "أي بهار يُستخرج من لحاء شجرة؟", "options": ["القرفة", "الكمون", "الفلفل", "الكركم"], "answer": 0, "level": 1, "spice": "قرفة", "hint": "لحاء مجفف ملفوف"},
    {"id": 3, "question": "ما المركب المسؤول عن حرارة الفلفل الحار؟", "options": ["الكابسيسين", "الكركمين", "البيبرين", "الأوجينول"], "answer": 0, "level": 2, "spice": "فلفل حار", "hint": "يبدأ بحرف الكاف"},
    {"id": 4, "question": "الزعفران يُستخرج من؟", "options": ["ميسم الزهرة", "البذور", "الجذور", "اللحاء"], "answer": 0, "level": 3, "spice": "زعفران", "hint": "أغلى بهار في العالم، 3 خيوط لكل زهرة"},
    {"id": 5, "question": "كم زهرة زعفران لإنتاج 1 غرام؟", "options": ["حوالي 150 زهرة", "20 زهرة", "50 زهرة", "500 زهرة"], "answer": 0, "level": 3, "spice": "زعفران", "hint": "رقم كبير جدا"},
    {"id": 6, "question": "الكمون ينتمي لعائلة؟", "options": ["الخيمية", "الزنجبيلية", "الفلفلية", "الغارية"], "answer": 0, "level": 2, "spice": "كمون", "hint": "نفس عائلة الكزبرة والشمر"},
    {"id": 7, "question": "أي بهار كان يُستخدم كعملة قديما؟", "options": ["الفلفل الأسود", "الملح", "القرفة", "القرنفل"], "answer": 0, "level": 2, "spice": "فلفل أسود", "hint": "في روما كان أغلى من الذهب وزن بوزن"},
    {"id": 8, "question": "الكركم يحتوي على؟", "options": ["الكركمين", "الكابسيسين", "المنثول", "الثيمول"], "answer": 0, "level": 1, "spice": "كركم", "hint": "مضاد التهاب قوي"},
    {"id": 9, "question": "ما هي بهارات الغارام ماسالا؟", "options": ["خلطة هندية حارة", "بهار واحد", "نوع فلفل", "ملح هندي"], "answer": 0, "level": 2, "spice": "غارام ماسالا", "hint": "كلمة تعني المزيج الحار"},
    {"id": 10, "question": "الهيل يُسمى في الخليج؟", "options": ["الهال", "الحبهان فقط", "القاعقلة", "كل ما سبق صحيح"], "answer": 3, "level": 1, "spice": "هيل", "hint": "له عدة أسماء عربية"},
    {"id": 11, "question": "أفضل هيل في العالم من؟", "options": ["غواتيمالا والهند", "روسيا", "كندا", "البرازيل"], "answer": 0, "level": 2, "spice": "هيل", "hint": "أمريكا الوسطى وجنوب آسيا"},
    {"id": 12, "question": "القرنفل هو؟", "options": ["برعم زهرة مجفف", "بذرة", "جذر", "ورقة"], "answer": 0, "level": 1, "spice": "قرنفل", "hint": "شكله مثل مسمار صغير"},
    {"id": 13, "question": "جوزة الطيب موطنها الأصلي؟", "options": ["جزر الملوك بإندونيسيا", "المغرب", "الهند", "إسبانيا"], "answer": 0, "level": 2, "spice": "جوزة الطيب", "hint": "جزر التوابل التاريخية"},
    {"id": 14, "question": "ما الفرق بين القرفة السيلانية والصينية؟", "options": ["السيلانية أرق وأحلى", "لا فرق", "الصينية أغلى", "السيلانية حارة جدا"], "answer": 0, "level": 3, "spice": "قرفة", "hint": "السيلانية True Cinnamon"},
    {"id": 15, "question": "السماق يُستخدم أساسا في؟", "options": ["المطبخ الشامي لإضافة حموضة", "الحلويات", "المشروبات الغازية", "صناعة الخبز فقط"], "answer": 0, "level": 1, "spice": "سماق", "hint": "بديل الليمون"},
    {"id": 16, "question": "الفلفل الوردي هو؟", "options": ["ليس فلفل حقيقي بل ثمرة شجرة", "فلفل أسود مصبوغ", "نوع فلفل حار", "خليط بهارات"], "answer": 0, "level": 3, "spice": "فلفل وردي", "hint": "من شجرة Schinus"},
    {"id": 17, "question": "الزعتر البري يحتوي على؟", "options": ["الثيمول", "الكافيين", "النيكوتين", "الكلوروفيل فقط"], "answer": 0, "level": 2, "spice": "زعتر", "hint": "مطهر طبيعي قوي"},
    {"id": 18, "question": "البابريكا تُصنع من؟", "options": ["فلفل حلو مجفف مطحون", "طماطم مجففة", "فلفل أسود", "كركم"], "answer": 0, "level": 1, "spice": "بابريكا", "hint": "هنغاريا مشهورة بها"},
    {"id": 19, "question": "ما هو البهار الذي يمنع نمو البكتيريا تاريخيا؟", "options": ["القرنفل", "السكر", "الملح فقط", "الخل فقط"], "answer": 0, "level": 2, "spice": "قرنفل", "hint": "استخدم في تحنيط وحفظ اللحوم"},
    {"id": 20, "question": "الكزبرة: الأوراق والبذور لهما؟", "options": ["نكهتان مختلفتان تماما", "نفس النكهة", "الأوراق بلا نكهة", "البذور سامة"], "answer": 0, "level": 2, "spice": "كزبرة", "hint": "ظاهرة معروفة"},
    {"id": 21, "question": "الشمر يشبه في الطعم؟", "options": ["اليانسون", "الفلفل", "القرفة", "الكركم"], "answer": 0, "level": 1, "spice": "شمر", "hint": "نكهة عرق السوس"},
    {"id": 22, "question": "طريق الحرير كان أساسا لنقل؟", "options": ["الحرير والتوابل", "الذهب فقط", "الخشب فقط", "الأسماك"], "answer": 0, "level": 1, "spice": "عام", "hint": "تجارة التوابل غيرت العالم"},
    {"id": 23, "question": "من احتكر تجارة جوزة الطيب 200 سنة؟", "options": ["الهولنديون", "البرتغاليون", "العرب", "الصينيون"], "answer": 0, "level": 3, "spice": "جوزة الطيب", "hint": "شركة الهند الشرقية الهولندية"},
    {"id": 24, "question": "الفلفل الأبيض هو؟", "options": ["فلفل أسود مقشر", "نوع مختلف تماما", "فلفل غير ناضج", "ملح وفلفل"], "answer": 0, "level": 2, "spice": "فلفل أبيض", "hint": "نفس الثمرة بدون القشرة السوداء"},
    {"id": 25, "question": "ما البهار المسمى الذهب الأسود قديما؟", "options": ["الفلفل الأسود", "الكمون الأسود", "حبة البركة", "السمسم الأسود"], "answer": 0, "level": 1, "spice": "فلفل أسود", "hint": "أغلى من الذهب"},
    {"id": 26, "question": "الكراوية تُستخدم لتخفيف؟", "options": ["المغص والانتفاخ", "الصداع فقط", "الحروق", "الكسور"], "answer": 0, "level": 1, "spice": "كراوية", "hint": "للأطفال تقليديا"},
    {"id": 27, "question": "حبة البركة ذكرت في؟", "options": ["الطب النبوي", "الطب الصيني فقط", "الطب اليوناني فقط", "لا ذكر لها"], "answer": 0, "level": 1, "spice": "حبة البركة", "hint": "شفاء من كل داء إلا السام"},
    {"id": 28, "question": "اليانسون النجمي موطنه؟", "options": ["الصين وفيتنام", "المغرب", "إيطاليا", "كندا"], "answer": 0, "level": 2, "spice": "يانسون نجمي", "hint": "آسيا"},
    {"id": 29, "question": "ما هي أقوى بهارات حرارة سكوفيل؟", "options": ["كارولاينا ريبر", "فلفل أسود", "بابريكا", "قرفة"], "answer": 0, "level": 2, "spice": "فلفل خارق", "hint": "أكثر من 2 مليون سكوفيل"},
    {"id": 30, "question": "الخردل كان يُستخدم كـ؟", "options": ["سلاح كيميائي بسيط قديما", "حلوى", "مشروب", "طلاء"], "answer": 0, "level": 3, "spice": "خردل", "hint": "غاز الخردل"},
    {"id": 31, "question": "ما البهار الذي يحسن الذاكرة حسب دراسات؟", "options": ["إكليل الجبل (روزماري)", "الملح", "السكر", "الفلفل"], "answer": 0, "level": 2, "spice": "روزماري", "hint": "طلاب اليونان القدامى"},
    {"id": 32, "question": "الزنجبيل الطازج والمجفف؟", "options": ["نكهتان مختلفتان", "نفس النكهة", "المجفف بلا نكهة", "الطازج سام"], "answer": 0, "level": 2, "spice": "زنجبيل", "hint": "المجفف أحـر"},
    {"id": 33, "question": "ما هو بهار السبع بهارات الشامي؟", "options": ["خلطة 7 بهارات أساسية", "بهار واحد نادر", "نوع فلفل", "7 أنواع ملح"], "answer": 0, "level": 1, "spice": "سبع بهارات", "hint": "خلطة مشهورة في بلاد الشام"},
    {"id": 34, "question": "الفلفل الطويل كان شائع قبل؟", "options": ["الفلفل الأسود", "الملح", "السكر", "القرفة"], "answer": 0, "level": 3, "spice": "فلفل طويل", "hint": "في روما القديمة"},
    {"id": 35, "question": "ما علاقة البهارات بالتحنيط المصري؟", "options": ["استخدمت القرفة والقرنفل والمر", "لا علاقة", "استخدم الملح فقط", "استخدم الذهب فقط"], "answer": 0, "level": 2, "spice": "عام", "hint": "مواد حافظة طبيعية"},
    {"id": 36, "question": "الكركمين يمتص أفضل مع؟", "options": ["الفلفل الأسود (بيبرين)", "الماء فقط", "السكر", "الملح"], "answer": 0, "level": 3, "spice": "كركم", "hint": "يزيد الامتصاص 2000%"},
    {"id": 37, "question": "ما هو بهار الماسالا دوسا؟", "options": ["خلطة بطاطس جنوب هندية", "نوع شاي", "نوع خبز فقط", "مشروب"], "answer": 0, "level": 2, "spice": "ماسالا", "hint": "فطور جنوب الهند"},
    {"id": 38, "question": "الفلفل الحلو (Bell) أصله؟", "options": ["أمريكا الوسطى والجنوبية", "الهند", "أوروبا", "أفريقيا"], "answer": 0, "level": 1, "spice": "فلفل حلو", "hint": "مثل الطماطم والبطاطس"},
    {"id": 39, "question": "ما البهار الذي لونه أزرق نادر؟", "options": ["لا يوجد بهار أزرق طبيعي شائع", "فلفل أزرق", "قرفة زرقاء", "كمون أزرق"], "answer": 0, "level": 3, "spice": "عام", "hint": "الأزرق نادر في الطبيعة"},
    {"id": 40, "question": "الشطة التونسية (هريسة) أساسها؟", "options": ["فلفل حار وثوم وكمون", "طماطم فقط", "فلفل أسود فقط", "قرفة"], "answer": 0, "level": 1, "spice": "هريسة", "hint": "شمال أفريقيا"},
    {"id": 41, "question": "ما هو بديل الزعفران الرخيص؟", "options": ["العصفر (القرطم)", "الكركم فقط", "الفلفل", "لا بديل"], "answer": 0, "level": 2, "spice": "زعفران", "hint": "يُغش به كثيرا"},
    {"id": 42, "question": "بهار الكاري هو؟", "options": ["خلطة بريطانية مستوحاة من الهند", "بهار هندي واحد", "نوع فلفل", "ورقة شجرة"], "answer": 0, "level": 2, "spice": "كاري", "hint": "اختراع استعماري"},
    {"id": 43, "question": "أوراق الكاري تُستخدم؟", "options": ["طازجة في الطبخ الهندي", "مجففة فقط", "لا تُؤكل", "كشاي فقط"], "answer": 0, "level": 2, "spice": "أوراق كاري", "hint": "مثل ورق الغار"},
    {"id": 44, "question": "ما هو البهار المسبب للتنميل اللسان؟", "options": ["فلفل سيشوان", "فلفل أسود", "قرفة", "كمون"], "answer": 0, "level": 3, "spice": "فلفل سيشوان", "hint": "مخدر طبيعي"},
    {"id": 45, "question": "الكمون الأسود (حبة البركة) ليس كمون حقيقي؟", "options": ["صحيح، من عائلة مختلفة", "خطأ، هو كمون", "هو فلفل", "هو ملح"], "answer": 0, "level": 2, "spice": "حبة البركة", "hint": "تسمية خاطئة شائعة"},
    {"id": 46, "question": "ما أكثر دولة إنتاجا للفلفل الأسود اليوم؟", "options": ["فيتنام", "الهند", "البرازيل", "إندونيسيا"], "answer": 0, "level": 2, "spice": "فلفل أسود", "hint": "آسيا جنوب شرق"},
    {"id": 47, "question": "بهار السوماخ (Sumac) لونه؟", "options": ["أحمر داكن", "أخضر", "أصفر", "أزرق"], "answer": 0, "level": 1, "spice": "سماق", "hint": "مثل التوت المجفف"},
    {"id": 48, "question": "ما هو البهار الذي كان يُهدى للملوك؟", "options": ["الزعفران والقرنفل", "الملح فقط", "السكر فقط", "الخل"], "answer": 0, "level": 1, "spice": "زعفران", "hint": "رمز الثراء"},
    {"id": 49, "question": "الفانيليا هي؟", "options": ["ثمرة أوركيد مجففة", "بذرة شجرة", "جذر", "لحاء"], "answer": 0, "level": 2, "spice": "فانيليا", "hint": "ثاني أغلى بهار بعد الزعفران"},
    {"id": 50, "question": "ما سر خلطة بهارات BSF الأسطورية؟", "options": ["حب + توازن + تجربة + صبر", "ملح فقط", "فلفل فقط", "سر لا يُكشف"], "answer": 0, "level": 5, "spice": "BSF Secret", "hint": "السر في القلب وليس المكونات"},
]

HISHAM_PUZZLES: List[Dict[str, Any]] = [
    {
        "stage": 1,
        "title": "بوابة القصر - The Palace Gate",
        "title_ar": "بوابة قصر هشام الأموي",
        "historical_fact": "قصر هشام بن عبد الملك، بني 724-743م قرب أريحا، نموذج العمارة الأموية المبكرة.",
        "puzzle": "أنا مدينة التمور والبهارات، بنيت على الماء وكنت محطة قوافل، من أنا؟ (4 حروف)",
        "answer": ["اريحا", "أريحا"],
        "hint": "أخفض مدينة في العالم",
        "reward_xp": 100,
    },
    {
        "stage": 2,
        "title": "قاعة الاستقبال - The Audience Hall",
        "title_ar": "قاعة شجرة الحياة الشهيرة",
        "historical_fact": "فسيفساء شجرة الحياة في قصر هشام هي أكبر فسيفساء متصلة في الشرق الأوسط، 827م².",
        "puzzle": "شجرة بلا أوراق، تمثل الحياة والموت والسلام في فسيفساء واحدة، ما اسم الرمز؟",
        "answer": ["شجرة الحياة", "شجره الحياه", "tree of life"],
        "hint": "غزال يهاجمه أسد تحت الشجرة",
        "reward_xp": 200,
    },
    {
        "stage": 3,
        "title": "الحمامات الأموية - Umayyad Baths",
        "title_ar": "حمامات قصر هشام - تطور هندسي",
        "historical_fact": "الحمامات استخدمت نظام تدفئة تحت الأرض (Hypocaust) روماني مطور.",
        "puzzle": "نظام تدفئة روماني، نار تحت الأرض تدفئ القصر، ما اسمه؟",
        "answer": ["هيبوكوست", "hypocaust", "تدفئة ارضية"],
        "hint": "يبدأ بـ H باللاتينية",
        "reward_xp": 300,
    },
    {
        "stage": 4,
        "title": "الكنز الأموي - The Umayyad Treasure",
        "title_ar": "كنز البهارات المفقود",
        "historical_fact": "الأمويون نقلوا بهارات الهند عبر أريحا إلى دمشق، طريق البخور الثاني.",
        "puzzle": "ما البهار الذي كان يُوزن بالذهب في دمشق الأموية وكان قادم من الملوك؟",
        "answer": ["زعفران", "الزعفران", "saffron"],
        "hint": "أغلى بهار، 3 مياسم لكل زهرة",
        "reward_xp": 500,
    },
]

PLAYABLE_CHARACTERS: Dict[str, Dict[str, Any]] = {
    "tiger": {
        "id": "tiger",
        "name": "نمر الأدغال",
        "name_en": "Jungle Tiger",
        "emoji": "🐯",
        "ability": "قفزة النمر",
        "ability_en": "Tiger Leap",
        "ability_type": AbilityType.JUMP,
        "ability_key": "jump",
        "cooldown": 3,
        "description": "يقفز فوق عقبة واحدة أو حفرة، يتجاهل التصادم لمرة واحدة",
        "description_en": "Leap over 1 obstacle - ignore collision once",
        "color": 0xFF8C00,
        "hp_bonus": 10,
    },
    "lion": {
        "id": "lion",
        "name": "أسد الصحراء",
        "name_en": "Desert Lion",
        "emoji": "🦁",
        "ability": "زئير الأسد",
        "ability_en": "Lion Roar",
        "ability_type": AbilityType.ROAR,
        "ability_key": "roar",
        "cooldown": 4,
        "description": "زئير يخيف الوحوش ضمن خليتين لمدة 10 ثواني",
        "description_en": "Scare monsters within 2 cells for 10s",
        "color": 0xFFD700,
        "hp_bonus": 20,
    },
    "mousa": {
        "id": "mousa",
        "name": "موسى الحكيم",
        "name_en": "Mousa The Wise",
        "emoji": "🧙‍♂️",
        "ability": "حكمة موسى",
        "ability_en": "Wisdom Hint",
        "ability_type": AbilityType.HINT,
        "ability_key": "hint",
        "cooldown": 2,
        "description": "يكشف تلميح إضافي للغز الصندوق القريب",
        "description_en": "Reveal extra hint for nearby riddle",
        "color": 0x8A2BE2,
        "hp_bonus": 0,
    },
    "worm": {
        "id": "worm",
        "name": "دودة الأرض الذكية",
        "name_en": "Smart Earthworm",
        "emoji": "🪱",
        "ability": "رادار الدودة",
        "ability_en": "Worm Radar",
        "ability_type": AbilityType.RADAR,
        "ability_key": "radar",
        "cooldown": 3,
        "description": "يظهر سهم يشير لأقرب صندوق كنز لمدة 5 ثواني",
        "description_en": "Show arrow to nearest treasure for 5s",
        "color": 0x8B4513,
        "hp_bonus": 5,
    },
    "tiger_hoodie": {
        "id": "tiger_hoodie",
        "name": "نمر الهودي",
        "name_en": "Hoodie Tiger",
        "emoji": "🐅",
        "ability": "اندفاع النمر",
        "ability_en": "Tiger Dash",
        "ability_type": AbilityType.DASH,
        "ability_key": "dash",
        "cooldown": 3,
        "description": "اندفاع خليتين للأمام بسرعة، يخترق عقبة",
        "description_en": "Dash 2 cells forward, pierce obstacle",
        "color": 0xFF4500,
        "hp_bonus": 15,
    },
    "lion_hoodie": {
        "id": "lion_hoodie",
        "name": "أسد الهودي",
        "name_en": "Hoodie Lion",
        "emoji": "🦁‍🟫",
        "ability": "درع الأسد",
        "ability_en": "Lion Shield",
        "ability_type": AbilityType.SHIELD,
        "ability_key": "shield",
        "cooldown": 5,
        "description": "درع يقلل الضرر 50% لمدة 12 ثانية",
        "description_en": "Shield -50% damage for 12s",
        "color": 0xDAA520,
        "hp_bonus": 30,
    },
}

MONSTERS: Dict[str, Dict[str, Any]] = {
    "spice_ghost": {"name": "شبح البهارات", "emoji": "👻", "damage": 15, "chase_range": 4, "speed": 1, "ai": "chaser"},
    "sand_worm": {"name": "دودة الرمل", "emoji": "🐛", "damage": 20, "chase_range": 5, "speed": 1, "ai": "chaser"},
    "desert_scorpion": {"name": "عقرب الصحراء", "emoji": "🦂", "damage": 25, "chase_range": 3, "speed": 1, "ai": "ambusher"},
    "palace_guard": {"name": "حارس القصر", "emoji": "🗿", "damage": 30, "chase_range": 6, "speed": 1, "ai": "chaser"},
}

TREASURE_BOXES: List[Dict[str, Any]] = [
    {"id": "box_1", "riddle": "أنا بهار أسود وملك الموائد، حار لطيف، من أنا؟", "answer": ["فلفل", "فلفل اسود"], "reward": "50xp + مفتاح برونزي"},
    {"id": "box_2", "riddle": "أصفر ذهبي، دواء وبهار، أصبغ الأرز؟", "answer": ["كركم", "كركمين"], "reward": "100xp + خريطة"},
    {"id": "box_3", "riddle": "من 3 حروف، أغلى بهار، زهرة بنفسجية؟", "answer": ["زعفران"], "reward": "250xp + تاج البهارات"},
]

MAP_TEMPLATE: List[str] = [
    "▓▓▓▓▓▓▓▓▓▓▓",
    "▓· · · ⬜ · · · ▓",
    "▓· ▓ · · · ▓ · ▓",
    "▓· · 👾 · · · · ▓",
    "▓· ▓ · ▓ · ▓ · ▓",
    "▓· · · · P · · · ▓",
    "▓· ▓ · ▓ · ▓ · ▓",
    "▓· · 🎁 · ⬜ · · ▓",
    "▓· ▓ · · · ▓ · ▓",
    "▓· · · 🎁 · · · ▓",
    "▓▓▓▓▓▓▓▓▓▓▓",
]

SOUNDS: Dict[str, Dict[str, str]] = {
    "move": {"file": "step.mp3", "desc": "حركة لاعب"},
    "obstacle_move": {"file": "stone_slide.mp3", "desc": "تحرك العقبة"},
    "monster_near": {"file": "growl.mp3", "desc": "وحش قريب - تحذير"},
    "monster_hit": {"file": "hit.mp3", "desc": "اصطدام وحش"},
    "ability_jump": {"file": "whoosh.mp3", "desc": "قفزة النمر"},
    "ability_roar": {"file": "roar.mp3", "desc": "زئير الأسد"},
    "ability_shield": {"file": "shield.mp3", "desc": "تفعيل الدرع"},
    "box_open": {"file": "chest.mp3", "desc": "فتح صندوق"},
    "level_up": {"file": "levelup.mp3", "desc": "ترقية مستوى"},
    "correct": {"file": "correct.mp3", "desc": "إجابة صحيحة"},
    "wrong": {"file": "wrong.mp3", "desc": "إجابة خاطئة"},
}

# ─────────────────────────────────────────────
# UserDataService - مع Redis Fallback احترافي
# ─────────────────────────────────────────────
class UserDataService:
    """
    Professional user data service with Redis primary and memory fallback.

    Attributes:
        redis_client: Optional Redis client.
        _memory_store: In-memory fallback dict.
        _lock: Async lock for memory store.
    """

    def __init__(self, redis_url: Optional[str] = None) -> None:
        self.redis_client: Optional[Any] = None
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._redis_url = redis_url or "redis://localhost:6379/0"
        self._connected = False

    async def initialize(self) -> None:
        """Initialize Redis connection with graceful fallback."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis lib not available, using memory store only")
            return
        try:
            self.redis_client = redis.from_url(self._redis_url, decode_responses=True)
            await self.redis_client.ping()
            self._connected = True
            logger.info("✅ Redis connected - UserDataService ready")
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}), falling back to memory")
            self.redis_client = None
            self._connected = False

    def _make_key(self, user_id: int, guild_id: int) -> str:
        return f"bsf:user:{guild_id}:{user_id}"

    async def get_user(self, user_id: int, guild_id: int) -> Dict[str, Any]:
        """Get user data with fallback."""
        key = self._make_key(user_id, guild_id)
        # Try Redis first
        if self.redis_client and self._connected:
            try:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
        # Fallback to memory
        async with self._lock:
            return self._memory_store.get(key, {
                "xp": 0,
                "level": 1,
                "baharat_score": 0,
                "hisham_progress": 0,
                "treasures": [],
                "character": "tiger",
                "created_at": datetime.utcnow().isoformat(),
            })

    async def save_user(self, user_id: int, guild_id: int, data: Dict[str, Any]) -> bool:
        """Save user data with error handling."""
        key = self._make_key(user_id, guild_id)
        try:
            if self.redis_client and self._connected:
                await self.redis_client.set(key, json.dumps(data, ensure_ascii=False), ex=86400*30)
                return True
        except Exception as e:
            logger.error(f"Redis save failed: {e} - using memory")

        async with self._lock:
            self._memory_store[key] = data
        return True

    async def add_xp(self, user_id: int, guild_id: int, amount: int) -> Tuple[int, bool]:
        """
        Add XP and check level up.

        Returns:
            Tuple of (new_level, leveled_up)
        """
        user = await self.get_user(user_id, guild_id)
        user["xp"] = user.get("xp", 0) + amount

        old_level = user.get("level", 1)
        new_level = old_level
        # Calculate level based on BAHARAT_LEVELS
        for lvl in reversed(BAHARAT_LEVELS):
            if user["xp"] >= lvl["xp_required"]:
                new_level = lvl["id"]
                break

        user["level"] = new_level
        await self.save_user(user_id, guild_id, user)
        return new_level, new_level > old_level

# Global service instance
user_service = UserDataService()

# ─────────────────────────────────────────────
# MapRenderer - مع دعم العقبات المتحركة
# ─────────────────────────────────────────────
class MapRenderer:
    """
    Professional map renderer with moving obstacles and entity layering.

    Supports:
        - Dynamic obstacle movement
        - Player, monsters, treasures layering
        - Emoji-based rendering for Discord
        - Collision map generation
    """

    def __init__(self, width: int = MAP_WIDTH, height: int = MAP_HEIGHT) -> None:
        self.width = width
        self.height = height
        self.base_map: List[List[str]] = [["·" for _ in range(width)] for _ in range(height)]
        self._init_walls()

    def _init_walls(self) -> None:
        """Initialize border walls."""
        for x in range(self.width):
            self.base_map[0][x] = "▓"
            self.base_map[self.height-1][x] = "▓"
        for y in range(self.height):
            self.base_map[y][0] = "▓"
            self.base_map[y][self.width-1] = "▓"

    def render(
        self,
        player: PlayerSession,
        obstacles: List[ObstacleState],
        monsters: List[MonsterState],
        treasures: List[TreasureBox],
        radar_arrow: Optional[str] = None,
        show_danger: bool = False,
    ) -> str:
        """
        Render full map to string for Discord embed.

        Args:
            player: Current player session
            obstacles: List of moving obstacles
            monsters: List of monsters
            treasures: List of treasure boxes
            radar_arrow: Optional directional arrow from worm ability
            show_danger: Whether to show danger warning

        Returns:
            Formatted map string with legend
        """
        # Clone base map
        grid = [row[:] for row in self.base_map]

        # Place obstacles (moving)
        for obs in obstacles:
            if 0 <= obs.pos.y < self.height and 0 <= obs.pos.x < self.width:
                grid[obs.pos.y][obs.pos.x] = obs.symbol

        # Place treasures
        for box in treasures:
            if not box.is_opened and 0 <= box.pos.y < self.height:
                grid[box.pos.y][box.pos.x] = "🎁"

        # Place monsters
        for mon in monsters:
            if time.time() < mon.scared_until:
                continue  # scared monsters hidden
            if 0 <= mon.pos.y < self.height:
                grid[mon.pos.y][mon.pos.x] = mon.emoji

        # Place player (top layer)
        grid[player.pos.y][player.pos.x] = PLAYABLE_CHARACTERS[player.character_id]["emoji"]

        # Build string
        lines = ["".join(row) for row in grid]
        map_str = "\n".join(lines)

        # Add legend
        char_info = PLAYABLE_CHARACTERS[player.character_id]
        legend = (
            f"\n{char_info['emoji']} **{char_info['name']}** | ❤️ {player.health} | 🏆 {player.score}\n"
            f"📍 ({player.pos.x},{player.pos.y}) | 🎮 Moves: {player.moves_count}"
        )

        if radar_arrow:
            legend += f"\n{radar_arrow} أقرب صندوق!"

        if show_danger:
            legend += "\n⚠️ **وحش قريب!** Monster nearby!"

        if player.shield_active and time.time() < player.shield_expires:
            remaining = int(player.shield_expires - time.time())
            legend += f"\n🛡️ درع نشط {remaining}s"

        return f"```\n{map_str}\n```{legend}"

    def is_walkable(self, pos: Position, obstacles: List[ObstacleState]) -> bool:
        """Check if position is walkable (not wall or obstacle)."""
        if pos.x <= 0 or pos.x >= self.width-1 or pos.y <= 0 or pos.y >= self.height-1:
            return False
        for obs in obstacles:
            if obs.pos.x == pos.x and obs.pos.y == pos.y:
                return False
        return True

# ─────────────────────────────────────────────
# GameLogic - منطق اللعبة مع moving obstacles + monster AI
# ─────────────────────────────────────────────
class GameLogic:
    """
    Core game logic handling entity movements.

    Key Feature - move_entities():
        Called every player move (turn-based), moves obstacles and monsters.
    """

    def __init__(self, renderer: MapRenderer) -> None:
        self.renderer = renderer

    def move_entities(
        self,
        player: PlayerSession,
        obstacles: List[ObstacleState],
        monsters: List[MonsterState],
        treasures: List[TreasureBox],
    ) -> Dict[str, Any]:
        """
        Move all dynamic entities - called every player turn.

        - Obstacles move every turn (turn-based moving obstacles)
        - Monsters use chasing AI towards player if in range

        Returns:
            Dict with events (collisions, warnings)
        """
        events: Dict[str, Any] = {"obstacle_moves": [], "monster_moves": [], "warnings": []}

        # 1. Move obstacles - حركة العقبات كل دور
        for obs in obstacles:
            if not obs.movable:
                continue
            # Randomly change direction 30% chance + move
            if random.random() < 0.3:
                obs.direction = random.choice(list(Direction))

            new_pos = obs.pos + obs.direction.value
            # Check bounds and avoid stacking
            if self.renderer.is_walkable(new_pos, [o for o in obstacles if o != obs]):
                # Avoid player pos? obstacles can push player (collision)
                obs.pos = new_pos
                events["obstacle_moves"].append(f"{obs.symbol}→({new_pos.x},{new_pos.y})")

        # 2. Monster AI - Chasing logic
        for mon in monsters:
            # Skip if scared (roar ability)
            if time.time() < mon.scared_until:
                continue

            dist = mon.pos.distance_to(player.pos)
            if dist <= mon.chase_range:
                # Chase player - move 1 step closer
                dx = 0
                dy = 0
                if mon.pos.x < player.pos.x:
                    dx = 1
                elif mon.pos.x > player.pos.x:
                    dx = -1
                if mon.pos.y < player.pos.y:
                    dy = 1
                elif mon.pos.y > player.pos.y:
                    dy = -1

                # Prefer horizontal or vertical randomly if both
                if dx != 0 and dy != 0:
                    if random.random() < 0.5:
                        dy = 0
                    else:
                        dx = 0

                new_mon_pos = Position(mon.pos.x + dx, mon.pos.y + dy)
                if self.renderer.is_walkable(new_mon_pos, obstacles):
                    mon.pos = new_mon_pos
                    events["monster_moves"].append(f"{mon.emoji} chase")

                # Check if now adjacent - warning
                if mon.pos.distance_to(player.pos) <= 2:
                    events["warnings"].append(f"{mon.emoji} قريب جدا!")

        # 3. Check obstacle collision with player after move
        for obs in obstacles:
            if obs.pos.x == player.pos.x and obs.pos.y == player.pos.y:
                events["warnings"].append("🪨 اصطدمت بك عقبة متحركة!")
                # Push player back or damage? For now damage
                if not (player.shield_active and time.time() < player.shield_expires):
                    player.health -= 10
                else:
                    player.health -= 5  # shield reduces

        return events

    def try_apply_ability(
        self,
        player: PlayerSession,
        ability_key: str,
        obstacles: List[ObstacleState],
        monsters: List[MonsterState],
        treasures: List[TreasureBox],
    ) -> Tuple[bool, str]:
        """
        Apply character ability with cooldown check.

        Returns:
            (success, message)
        """
        now = time.time()
        char = PLAYABLE_CHARACTERS[player.character_id]

        # Check cooldown
        if ability_key in player.ability_cooldowns:
            if now < player.ability_cooldowns[ability_key]:
                remaining = int(player.ability_cooldowns[ability_key] - now)
                return False, f"⏳ القدرة جاهزة بعد {remaining} ثانية"

        # Apply by type
        if ability_key == "jump":  # Tiger
            # Jump over obstacle in facing? For simplicity, allow next move ignore obstacle
            player.inventory.append("jump_ready")
            msg = "🦘 قفزة جاهزة! الحركة القادمة تتجاهل عقبة"
        elif ability_key == "roar":  # Lion
            affected = 0
            for mon in monsters:
                if mon.pos.distance_to(player.pos) <= 2:
                    mon.scared_until = now + 10.0
                    affected += 1
            msg = f"🦁 زئير! أخفت {affected} وحوش لمدة 10 ثواني"
        elif ability_key == "hint":  # Mousa
            # Find nearest treasure
            nearest = min(treasures, key=lambda t: t.pos.distance_to(player.pos), default=None)
            if nearest:
                msg = f"💡 تلميح: {nearest.riddle[:30]}... الجواب يبدأ بـ {nearest.answer[0][:2]}"
            else:
                msg = "💡 لا يوجد صندوق قريب"
        elif ability_key == "radar":  # Worm
            nearest = min(treasures, key=lambda t: t.pos.distance_to(player.pos), default=None)
            if nearest:
                dx = nearest.pos.x - player.pos.x
                dy = nearest.pos.y - player.pos.y
                arrow = "➡️" if abs(dx) > abs(dy) and dx > 0 else "⬅️" if abs(dx) > abs(dy) else "⬇️" if dy > 0 else "⬆️"
                msg = f"{arrow} الصندوق الأقرب في اتجاه {arrow}"
            else:
                msg = "📡 لا يوجد كنز"
        elif ability_key == "dash":  # Tiger hoodie
            player.inventory.append("dash_ready")
            msg = "💨 اندفاع جاهز! ستتحرك خليتين"
        elif ability_key == "shield":  # Lion hoodie
            player.shield_active = True
            player.shield_expires = now + 12.0
            msg = "🛡️ درع الأسد نشط 12 ثانية - ضرر -50%"
        else:
            return False, "❌ قدرة غير معروفة"

        # Set cooldown
        cooldown_sec = char["cooldown"]
        player.ability_cooldowns[ability_key] = now + cooldown_sec
        return True, msg

# Global instances
map_renderer = MapRenderer()
game_logic = GameLogic(map_renderer)

# Active sessions - in-memory for performance
active_sessions: Dict[Tuple[int, int], PlayerSession] = {}
session_obstacles: Dict[Tuple[int, int], List[ObstacleState]] = {}
session_monsters: Dict[Tuple[int, int], List[MonsterState]] = {}
session_treasures: Dict[Tuple[int, int], List[TreasureBox]] = {}
session_radar: Dict[Tuple[int, int], str] = {}

# ─────────────────────────────────────────────
# Views - Discord UI
# ─────────────────────────────────────────────
class CharacterSelectView(discord.ui.View):
    """View for selecting playable character."""

    def __init__(self, user_id: int, guild_id: int) -> None:
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id
        self.selected: Optional[str] = None

        # Dynamically add buttons for each character
        for char_id, char in PLAYABLE_CHARACTERS.items():
            btn = discord.ui.Button(
                label=f"{char['name']} - {char['ability']}",
                emoji=char["emoji"],
                style=discord.ButtonStyle.secondary,
                custom_id=f"char_{char_id}",
            )
            btn.callback = self._make_callback(char_id)
            self.add_item(btn)

    def _make_callback(self, char_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ ليس لك!", ephemeral=True)
                return
            self.selected = char_id
            await interaction.response.send_message(
                f"✅ اخترت **{PLAYABLE_CHARACTERS[char_id]['name']}** {PLAYABLE_CHARACTERS[char_id]['emoji']}\n"
                f"قدرتك: {PLAYABLE_CHARACTERS[char_id]['description']}",
                ephemeral=True
            )
            self.stop()
            # Start game
            await self._start_game(interaction)

        return callback

    async def _start_game(self, interaction: discord.Interaction) -> None:
        """Initialize game session after character selection."""
        key = (self.user_id, self.guild_id)
        # Create player at center
        player = PlayerSession(
            user_id=self.user_id,
            guild_id=self.guild_id,
            character_id=self.selected or "tiger",
            pos=Position(MAP_WIDTH//2, MAP_HEIGHT//2),
            health=100 + PLAYABLE_CHARACTERS[self.selected or "tiger"].get("hp_bonus", 0),
        )
        active_sessions[key] = player

        # Create moving obstacles - 4 obstacles moving each turn
        obstacles = [
            ObstacleState(Position(2, 2), Direction.RIGHT, "🪨"),
            ObstacleState(Position(8, 3), Direction.LEFT, "⬜"),
            ObstacleState(Position(3, 7), Direction.DOWN, "🪨"),
            ObstacleState(Position(7, 8), Direction.UP, "🌵"),
        ]
        session_obstacles[key] = obstacles

        # Create monsters with chasing AI
        monsters = [
            MonsterState("m1", Position(1, 3), "spice_ghost", chase_range=5, emoji="👻"),
            MonsterState("m2", Position(9, 9), "sand_worm", chase_range=6, emoji="🐛"),
            MonsterState("m3", Position(5, 1), "desert_scorpion", chase_range=4, emoji="🦂"),
        ]
        session_monsters[key] = monsters

        # Create treasures
        treasures = [
            TreasureBox("box_1", Position(2, 7), TREASURE_BOXES[0]["riddle"], TREASURE_BOXES[0]["answer"][0], 50, "مفتاح برونزي"),
            TreasureBox("box_2", Position(8, 2), TREASURE_BOXES[1]["riddle"], TREASURE_BOXES[1]["answer"][0], 100, "خريطة"),
            TreasureBox("box_3", Position(5, 9), TREASURE_BOXES[2]["riddle"], TREASURE_BOXES[2]["answer"][0], 250, "تاج"),
        ]
        session_treasures[key] = treasures

        # Send game view
        embed = discord.Embed(
            title=f"🗺️ بدأت مغامرة {PLAYABLE_CHARACTERS[player.character_id]['name']}",
            description=map_renderer.render(player, obstacles, monsters, treasures),
            color=PLAYABLE_CHARACTERS[player.character_id]["color"],
        )
        embed.set_footer(text="استخدم الأزرار للحركة والقدرات - العقبات تتحرك كل دور!")

        view = GameView(self.user_id, self.guild_id)
        await interaction.followup.send(embed=embed, view=view)

class GameView(discord.ui.View):
    """
    Main game view with 5 movement buttons + ability buttons.

    Features:
        - Up/Down/Left/Right/Open
        - Ability buttons per character that actually work
        - move() calls GameLogic.move_entities() to move obstacles and monsters
        - Collision checks and warnings
    """

    def __init__(self, user_id: int, guild_id: int) -> None:
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.key = (user_id, guild_id)

    def _get_session_data(self):
        return (
            active_sessions.get(self.key),
            session_obstacles.get(self.key, []),
            session_monsters.get(self.key, []),
            session_treasures.get(self.key, []),
        )

    async def _update_map(self, interaction: discord.Interaction, events: Optional[Dict] = None, extra_msg: str = "") -> None:
        player, obstacles, monsters, treasures = self._get_session_data()
        if not player:
            await interaction.response.send_message("❌ انتهت الجلسة", ephemeral=True)
            return

        show_danger = False
        if events and events.get("warnings"):
            show_danger = True
            extra_msg += "\n" + "\n".join(events["warnings"])

        radar = session_radar.get(self.key)
        map_str = map_renderer.render(player, obstacles, monsters, treasures, radar_arrow=radar, show_danger=show_danger)

        # Check monster collision - damage
        for mon in monsters:
            if mon.pos.x == player.pos.x and mon.pos.y == player.pos.y and time.time() > mon.scared_until:
                dmg = mon.damage
                if player.shield_active and time.time() < player.shield_expires:
                    dmg = dmg // 2
                player.health -= dmg
                extra_msg += f"\n💥 {mon.emoji} هاجمك! -{dmg} صحة"

        embed = discord.Embed(
            title=f"🗺️ مغامرة البهارات - {PLAYABLE_CHARACTERS[player.character_id]['name']}",
            description=map_str + (f"\n\n{extra_msg}" if extra_msg else ""),
            color=PLAYABLE_CHARACTERS[player.character_id]["color"],
        )
        if player.health <= 0:
            embed.title = "💀 انتهت المغامرة"
            embed.description = f"خسرت! نقاطك: {player.score}\nاستخدم /treasure لبدء مغامرة جديدة"
            embed.color = 0xFF0000
            # Cleanup
            active_sessions.pop(self.key, None)
            self.stop()
        else:
            # Check treasure nearby for open
            for box in treasures:
                if not box.is_opened and box.pos.distance_to(player.pos) <= 1:
                    embed.add_field(name="🎁 صندوق قريب!", value=f"اضغط Open - {box.riddle[:50]}...", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    async def _handle_move(self, interaction: discord.Interaction, direction: Direction) -> None:
        """Core move logic - calls GameLogic.move_entities()"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ ليس دورك", ephemeral=True)
            return

        player, obstacles, monsters, treasures = self._get_session_data()
        if not player:
            await interaction.response.send_message("❌ لا يوجد جلسة", ephemeral=True)
            return

        # Check for jump/dash ability ready
        jump_ready = "jump_ready" in player.inventory
        dash_ready = "dash_ready" in player.inventory
        steps = 2 if dash_ready else 1

        # Calculate target
        target_pos = player.pos
        blocked = False
        for _ in range(steps):
            next_pos = target_pos + direction.value
            # Check walkable
            if not map_renderer.is_walkable(next_pos, obstacles) and not jump_ready and not dash_ready:
                blocked = True
                break
            target_pos = next_pos
            # If jump, consume after first obstacle ignore
            if jump_ready:
                player.inventory.remove("jump_ready")
                jump_ready = False
            if dash_ready:
                # dash consumes after move
                pass

        if blocked:
            await interaction.response.send_message("🧱 عقبة! استخدم قدرة النمر للقفز", ephemeral=True)
            return

        # Move player
        player.pos = target_pos
        player.moves_count += 1

        # Consume dash
        if dash_ready and "dash_ready" in player.inventory:
            player.inventory.remove("dash_ready")

        # ⬇️ Critical: Move obstacles and monsters every player move (turn-based)
        events = game_logic.move_entities(player, obstacles, monsters, treasures)

        # Clear radar after 5 sec? We handle via timeout in ability but keep for display
        # Save sessions
        active_sessions[self.key] = player
        session_obstacles[self.key] = obstacles
        session_monsters[self.key] = monsters

        extra = ""
        if events.get("obstacle_moves"):
            extra += f"🪨 تحركت {len(events['obstacle_moves'])} عقبات! "
        if events.get("monster_moves"):
            extra += f"👾 {len(events['monster_moves'])} وحوش تتبعك! "

        await self._update_map(interaction, events, extra)

    @discord.ui.button(label="⬆️ Up", style=discord.ButtonStyle.primary, row=0)
    async def btn_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_move(interaction, Direction.UP)

    @discord.ui.button(label="⬇️ Down", style=discord.ButtonStyle.primary, row=0)
    async def btn_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_move(interaction, Direction.DOWN)

    @discord.ui.button(label="⬅️ Left", style=discord.ButtonStyle.primary, row=0)
    async def btn_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_move(interaction, Direction.LEFT)

    @discord.ui.button(label="➡️ Right", style=discord.ButtonStyle.primary, row=0)
    async def btn_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_move(interaction, Direction.RIGHT)

    @discord.ui.button(label="📦 Open", style=discord.ButtonStyle.success, row=0)
    async def btn_open(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ ليس لك", ephemeral=True)
            return
        await self.try_open(interaction)

    # Ability buttons - dynamically added in __init__ override? We'll add via decorator for each char
    # For simplicity, we add generic ability buttons that dispatch based on character

    @discord.ui.button(label="⚡ Ability 1", style=discord.ButtonStyle.secondary, row=1, custom_id="ability_main")
    async def btn_ability_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ ليس لك", ephemeral=True)
            return
        player = active_sessions.get(self.key)
        if not player:
            return
        char = PLAYABLE_CHARACTERS[player.character_id]
        ability_key = char["ability_key"]

        player_s, obstacles, monsters, treasures = self._get_session_data()
        success, msg = game_logic.try_apply_ability(player_s, ability_key, obstacles, monsters, treasures)

        # Handle radar arrow storage
        if ability_key == "radar" and success:
            # Determine arrow
            nearest = min(treasures, key=lambda t: t.pos.distance_to(player_s.pos), default=None)
            if nearest:
                dx = nearest.pos.x - player_s.pos.x
                dy = nearest.pos.y - player_s.pos.y
                if abs(dx) > abs(dy):
                    arrow = "➡️ صندوق شرقا" if dx > 0 else "⬅️ صندوق غربا"
                else:
                    arrow = "⬇️ صندوق جنوبا" if dy > 0 else "⬆️ صندوق شمالا"
                session_radar[self.key] = arrow
                # Auto clear after 5 sec
                async def clear_radar():
                    await asyncio.sleep(5)
                    session_radar.pop(self.key, None)
                asyncio.create_task(clear_radar())

        await self._update_map(interaction, extra_msg=msg if success else f"❌ {msg}")

    @discord.ui.button(label="🛡️ Ability 2", style=discord.ButtonStyle.secondary, row=1, custom_id="ability_second")
    async def btn_ability_second(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ ليس لك", ephemeral=True)
            return
        # For hoodie characters, second ability? For now same as main or shield check
        player = active_sessions.get(self.key)
        if not player:
            return
        # Only lion_hoodie has shield as main, tiger_hoodie dash etc - we allow hint for mousa as second?
        # Simple: if mousa, second ability is radar-like? We'll just re-trigger main with message
        await interaction.response.send_message("ℹ️ قدرتك الأساسية في الزر الأول - الكولداون يظهر عند الاستخدام", ephemeral=True)

    async def try_open(self, interaction: discord.Interaction) -> None:
        """
        Try to open treasure box with riddle.

        Shows riddle and waits for answer via modal.
        """
        player, obstacles, monsters, treasures = self._get_session_data()
        if not player:
            return

        # Find nearby box
        nearby_box = None
        for box in treasures:
            if not box.is_opened and box.pos.distance_to(player.pos) <= 1:
                nearby_box = box
                break

        if not nearby_box:
            await interaction.response.send_message("❌ لا يوجد صندوق قريب - اقترب أكثر!", ephemeral=True)
            return

        # Show riddle modal
        class RiddleModal(discord.ui.Modal, title="🎁 لغز صندوق الكنز"):
            riddle_answer = discord.ui.TextInput(
                label=f"اللغز: {nearby_box.riddle[:80]}",
                placeholder="اكتب جوابك هنا...",
                max_length=50,
            )

            async def on_submit(self, modal_inter: discord.Interaction):
                answer = self.riddle_answer.value.strip()
                # Check answer
                correct_answers = [a.strip() for a in nearby_box.answer.split(",")] if isinstance(nearby_box.answer, str) else nearby_box.answer
                # Also handle list
                if isinstance(nearby_box.answer, list):
                    correct_answers = nearby_box.answer
                is_correct = any(answer in ca or ca in answer for ca in correct_answers) or answer == nearby_box.answer

                # More lenient Arabic check
                normalized = answer.replace(" ", "").replace("ال", "")
                for ca in correct_answers if isinstance(correct_answers, list) else [nearby_box.answer]:
                    if isinstance(ca, str) and normalized in ca.replace(" ", "").replace("ال", ""):
                        is_correct = True

                if is_correct:
                    nearby_box.is_opened = True
                    player.score += nearby_box.reward_xp
                    player.inventory.append(nearby_box.reward_item)
                    # XP via service
                    await user_service.add_xp(player.user_id, player.guild_id, nearby_box.reward_xp)
                    await modal_inter.response.send_message(
                        f"✅ صحيح! فتحت الصندوق 🎉\n"
                        f"حصلت على: {nearby_box.reward_item} + {nearby_box.reward_xp} XP",
                        ephemeral=True
                    )
                else:
                    await modal_inter.response.send_message(
                        f"❌ خطأ! الجواب الصحيح كان: {nearby_box.answer}\n"
                        f"تلميح: {TREASURE_BOXES[0]['riddle'][:30] if nearby_box.id == 'box_1' else 'فكر في البهارات'}",
                        ephemeral=True
                    )

        await interaction.response.send_modal(RiddleModal())

# ─────────────────────────────────────────────
# Cogs - 4 ألعاب متكاملة
# ─────────────────────────────────────────────
class BaharatGame(commands.Cog):
    """لعبة اختبار البهارات - 50 سؤال احترافي"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="baharat", description="اختبر معلوماتك في البهارات - 50 سؤال")
    @app_commands.describe(level="اختر المستوى")
    async def baharat_quiz(self, interaction: discord.Interaction, level: int = 1) -> None:
        """Start baharat quiz with level filtering."""
        await interaction.response.defer()

        user_data = await user_service.get_user(interaction.user.id, interaction.guild_id or 0)
        # Filter questions by level
        filtered = [q for q in QUESTIONS if q["level"] <= level] or QUESTIONS
        question = random.choice(filtered)

        class QuizView(discord.ui.View):
            def __init__(self, q: Dict[str, Any]):
                super().__init__(timeout=30)
                self.q = q
                self.answered = False
                for idx, opt in enumerate(q["options"]):
                    btn = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.secondary, custom_id=f"opt_{idx}")
                    btn.callback = self._make_cb(idx)
                    self.add_item(btn)

            def _make_cb(self, idx: int):
                async def cb(inter: discord.Interaction):
                    if self.answered:
                        await inter.response.send_message("⏳ انتهى السؤال", ephemeral=True)
                        return
                    self.answered = True
                    is_correct = idx == self.q["answer"]
                    if is_correct:
                        new_lvl, leveled = await user_service.add_xp(inter.user.id, inter.guild_id or 0, 25)
                        msg = f"✅ **صحيح!** {self.q['spice']} - {self.q['hint']}"
                        if leveled:
                            msg += f"\n🎉 ترقية! الآن مستواك {new_lvl} - {BAHARAT_LEVELS[new_lvl-1]['name']}"
                    else:
                        correct = self.q["options"][self.q["answer"]]
                        msg = f"❌ خطأ! الجواب: **{correct}**\n💡 {self.q['hint']}"
                    # Disable buttons
                    for child in self.children:
                        child.disabled = True
                    await inter.response.edit_message(content=msg, view=self)
                    self.stop()
                return cb

        embed = discord.Embed(
            title=f"🌶️ سؤال بهارات - مستوى {level} | {question['spice']}",
            description=f"**{question['question']}**\n\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(question["options"])]),
            color=0xF59E0B,
        )
        embed.set_footer(text=f"سؤال {question['id']}/50 | تلميح: /baharat hint")
        await interaction.followup.send(embed=embed, view=QuizView(question))

    @app_commands.command(name="baharat_leaderboard", description="لوحة متصدري البهارات")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏆 لوحة الصدارة قريبا - Redis leaderboard", ephemeral=True)

class HishamPalace(commands.Cog):
    """مغامرة قصر هشام التاريخية - 4 مراحل"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.user_progress: Dict[Tuple[int, int], int] = {}

    @app_commands.command(name="hisham", description="ابدأ مغامرة قصر هشام الأموي التاريخي - 4 مراحل")
    async def start_hisham(self, interaction: discord.Interaction):
        await interaction.response.defer()
        key = (interaction.user.id, interaction.guild_id or 0)
        progress = self.user_progress.get(key, 0)  # 0-4
        if progress >= len(HISHAM_PUZZLES):
            progress = 0

        puzzle = HISHAM_PUZZLES[progress]

        embed = discord.Embed(
            title=f"🏛️ {puzzle['title_ar']} - المرحلة {puzzle['stage']}/4",
            description=(
                f"📜 **معلومة تاريخية:**\n{puzzle['historical_fact']}\n\n"
                f"🧩 **اللغز:**\n{puzzle['puzzle']}\n\n"
                f"💡 تلميح: {puzzle['hint']}"
            ),
            color=0x8B5CF6,
        )
        embed.set_footer(text="اكتب جوابك في المحادثة أو استخدم الزر")

        class HishamView(discord.ui.View):
            def __init__(self, cog: "HishamPalace", stage: int):
                super().__init__(timeout=120)
                self.cog = cog
                self.stage = stage

            @discord.ui.button(label="💡 تلميح إضافي", style=discord.ButtonStyle.secondary)
            async def hint_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                puz = HISHAM_PUZZLES[self.stage]
                await inter.response.send_message(f"💡 {puz['hint']} - الجواب من {len(puz['answer'][0])} حروف", ephemeral=True)

            @discord.ui.button(label="📜 معلومة القصر", style=discord.ButtonStyle.primary)
            async def info_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                puz = HISHAM_PUZZLES[self.stage]
                await inter.response.send_message(f"🏛️ {puz['historical_fact']}", ephemeral=True)

        view = HishamView(self, progress)

        await interaction.followup.send(embed=embed, view=view)

        # Wait for text answer
        def check(m: discord.Message):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel_id

        try:
            msg = await self.bot.wait_for("message", timeout=90, check=check)
            answer = msg.content.strip().lower()
            correct = any(ans in answer or answer in ans.lower() for ans in puzzle["answer"])

            if correct:
                self.user_progress[key] = progress + 1
                await user_service.add_xp(interaction.user.id, interaction.guild_id or 0, puzzle["reward_xp"])
                await interaction.followup.send(
                    f"✅ **أحسنت!** تقدمت للمرحلة {progress+2}/4\n"
                    f"🏆 +{puzzle['reward_xp']} XP\n"
                    f"{'🎉 أنهيت قصر هشام! حصلت على لقب مؤرخ أموي' if progress+1 >= len(HISHAM_PUZZLES) else 'استخدم /hisham للمرحلة التالية'}"
                )
            else:
                await interaction.followup.send(f"❌ ليس صحيحا، حاول مرة أخرى. الجواب يبدأ بـ {puzzle['answer'][0][:2]}")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ انتهى الوقت - استخدم /hisham مرة أخرى")

class TreasureHunt(commands.Cog):
    """لعبة صيد الكنز مع شخصيات وقدرات تعمل فعليا + عقبات متحركة"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="treasure", description="ابدأ مغامرة صيد الكنز - اختر شخصيتك وقدراتك")
    async def start_treasure(self, interaction: discord.Interaction):
        """Entry point - character selection then game view with abilities."""
        embed = discord.Embed(
            title="🗺️ اختر بطلك - صيد كنز البهارات",
            description=(
                "اختر شخصيتك - كل شخصية لها قدرة تعمل فعليا:\n\n" +
                "\n".join([
                    f"{c['emoji']} **{c['name']}** - {c['ability']}: {c['description']} (كولداون {c['cooldown']})"
                    for c in PLAYABLE_CHARACTERS.values()
                ]) +
                "\n\n⚠️ **جديد v2.5:** العقبات تتحرك كل دور! الوحوش تطاردك بذكاء!"
            ),
            color=0xF59E0B,
        )
        view = CharacterSelectView(interaction.user.id, interaction.guild_id or 0)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="map_debug", description="عرض خريطة debug للمطور")
    async def debug_map(self, interaction: discord.Interaction):
        key = (interaction.user.id, interaction.guild_id or 0)
        player = active_sessions.get(key)
        if not player:
            await interaction.response.send_message("❌ لا يوجد جلسة نشطة", ephemeral=True)
            return
        obstacles = session_obstacles.get(key, [])
        monsters = session_monsters.get(key, [])
        treasures = session_treasures.get(key, [])
        map_str = map_renderer.render(player, obstacles, monsters, treasures, show_danger=True)
        await interaction.response.send_message(map_str, ephemeral=True)

class SoundsCog(commands.Cog):
    """نظام الأصوات - SOUNDS مع وصف عربي"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="sounds", description="عرض مكتبة أصوات اللعبة")
    async def list_sounds(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔊 مكتبة الأصوات - BSF Bot", color=0x22C55E)
        for key, data in SOUNDS.items():
            embed.add_field(name=f"{key} - {data['desc']}", value=f"📁 {data['file']}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="play_sound", description="تشغيل صوت (محاكاة)")
    @app_commands.describe(sound="اسم الصوت")
    async def play_sound(self, interaction: discord.Interaction, sound: str):
        if sound not in SOUNDS:
            await interaction.response.send_message(f"❌ الصوت غير موجود. المتاح: {', '.join(SOUNDS.keys())}", ephemeral=True)
            return
        # In real bot, would play in voice or send file
        await interaction.response.send_message(f"🔊 تشغيل: {SOUNDS[sound]['file']} - {SOUNDS[sound]['desc']}", ephemeral=True)

class MapCog(commands.Cog):
    """خريطة عالم الدودة - Worm World Map"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="worm_map", description="عرض خريطة عالم الدودة الكامل")
    async def worm_world_map(self, interaction: discord.Interaction):
        """Render worm world map overview."""
        # Generate world map with biomes
        world_desc = (
            "```\n"
            "🪱 WORM WORLD - خريطة العالم\n"
            "▓▓▓ جبال البهارات ▓▓▓\n"
            "🌵🏜️ صحراء الكمون - وحوش: عقارب\n"
            "🌿🌶️ غابة الفلفل - وحوش: أشباح\n"
            "🏛️ قصر هشام - المرحلة النهائية\n"
            "🎁 3 صناديق كنز مخفية\n"
            "🪨 4 عقبات متحركة كل دور!\n"
            "```"
        )
        embed = discord.Embed(
            title="🗺️ خريطة عالم الدودة",
            description=world_desc + "\n\nاستخدم /treasure للبدء",
            color=0x8B4513,
        )
        await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
# Final Setup - تحميل كل الـ Cogs الأربعة
# ─────────────────────────────────────────────
async def setup(bot: commands.Bot) -> None:
    """
    Professional setup loading all 4 cogs.

    Called automatically by discord.py extension loader.
    Usage: await bot.load_extension('phrases') or baharat.py
    """
    # Initialize user service
    await user_service.initialize()

    # Add all 4 cogs - كما هو مطلوب
    await bot.add_cog(BaharatGame(bot))
    await bot.add_cog(HishamPalace(bot))
    await bot.add_cog(TreasureHunt(bot))
    await bot.add_cog(SoundsCog(bot))
    await bot.add_cog(MapCog(bot))

    logger.info("✅ BSF Bot v2.5.0 - All 4 cogs loaded:")
    logger.info("   • BaharatGame (50 questions)")
    logger.info("   • HishamPalace (4 stages historical)")
    logger.info("   • TreasureHunt (6 characters + moving obstacles + chasing AI)")
    logger.info("   • SoundsCog + MapCog")
    logger.info("🎮 Moving obstacles: enabled (turn-based)")
    logger.info("👾 Monster chasing AI: enabled")
    logger.info("⚡ Playable abilities: 6 working with cooldowns")

# ─────────────────────────────────────────────
# Optional: Standalone Bot Runner (للتطوير المحلي)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # For local testing only - لا تستخدم التوكن في الكود في الإنتاج
    import os

    intents = discord.Intents.default()
    intents.message_content = True

    class BSFBot(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix="!", intents=intents)

        async def setup_hook(self):
            await setup(self)
            # Sync commands
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} commands")
            except Exception as e:
                logger.error(f"Sync failed: {e}")

        async def on_ready(self):
            logger.info(f"🤖 Logged in as {self.user} - BSF v2.5.0 Ready!")

    bot = BSFBot()
    # bot.run(os.getenv("DISCORD_TOKEN"))  # ضع التوكن في .env
    print("⚠️ ضع DISCORD_TOKEN في متغيرات البيئة ثم شغل البوت")
