import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio

DATA_FILE = "bsf_data.json"
QUESTIONS_FILE = "questions.json"

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

def load_real_questions():
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                conv = []
                for q in raw:
                    conv.append({
                        "id": q.get("id", 0),
                        "q": q["q"],
                        "options": q["options"],
                        "answer": q["correct"],
                        "level": min((q.get("id",1)-1)//5, 9),
                        "type": "عام",
                        "info": q
