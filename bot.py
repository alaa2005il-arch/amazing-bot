import os
import random
import threading
from flask import Flask
import discord
from openai import OpenAI
from phrases import PHRASES, AI_SYSTEM

# سيرفر عشان Discloud ما يطفي
app = Flask(__name__)
@app.route('/')
def home():
    return "BSF Bot LIVE! احنا ال BSF احنا! 🔥"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# اعداد الذكاء الاصطناعي
ai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY")
)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ BSF LIVE: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content
    low = content.lower()

    # اذا حد كتب bsf
    if "bsf" in low:
        await message.channel.send(random.choice(PHRASES))

    # اذا حد كتب!موسى
    if content.startswith("!موسى"):
        سوال = content.replace("!موسى", "").strip()
        if not سوال:
            await message.channel.send("هلا يا زعيم! اكتب سؤالك بعد!موسى")
            return

        async with message.channel.typing():
            try:
                رد = ai_client.chat.completions.create(
                    model="google/gemini-flash-1.5-8b:free",
                    messages=[
                        {"role": "system", "content": AI_SYSTEM},
                        {"role": "user", "content": سوال}
                    ]
                )
                await message.channel.send(رد.choices[0].message.content)
            except Exception as e:
                print(f"AI Error: {e}")
                await message.channel.send("المخ علق شوي يا زعيم، جرب كمان مرة! 🗑️ سطل هو السبب")

# تشغيل
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client.run(token.strip())
    else:
        print("❌ DISCORD_TOKEN مش موجود")
