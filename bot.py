import discord
from discord.ext import commands
import os
import random
import asyncio

# ========== إعدادات BSF ==========
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="::", intents=intents)

BSF_PHRASES = [
    "👑 الزعيم المؤسس ابو عيسى أخو عجيب",
    "😴 معدن بضل أخوي حتى واحنا نايمين",
    "🔄 معدن لما يتحول موسى وينسى بصير اندي معدن",
    "🤝 كلنا BSF أصدقاء وإخوة للأبد"
]

# ========== ذكاء موسى ==========
async def ask_ai_for_musa(question):
    system = "انت موسى من BSF. العيلة: الزعيم المؤسس ابو عيسى أخو عجيب، عجيب، موسى، موشي العبقري، معدن، اندي معدن. معدن بضل أخوي حتى واحنا نايمين. كلنا BSF أصدقاء للأبد. جاوب بلهجة فلسطينية شبابية مختصرة وحط ايموجي."
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No key")
        client = openai.AsyncOpenAI(api_key=api_key)
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": question}]
        )
        return res.choices[0].message.content
    except:
        answers = [
            f"سألت عن '{question}'؟ موسى بقول: روح اسأل الزعيم المؤسس ابو عيسى أخو عجيب 👑",
            f"بالنسبة لـ '{question}' - معدن بضل أخوي حتى واحنا نايمين 😴",
