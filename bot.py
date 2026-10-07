import os
import asyncio
import discord
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
load_dotenv()

RESPONSE_TEXT = "BSF بزعامة عجيب وابو عيسى 👑🔥💣"
TRIGGER_WORDS = ["BSF", "بزعامة", "عجيب", "ابو عيسى"]

def is_bsf_message(text: str):
    if not text: return False
    text_lower = text.lower()
    return any(word.lower() in text_lower for word in TRIGGER_WORDS)

async def run_discord():
    try:
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            print(f'✅ DISCORD LIVE: {client.user}')
            await client.change_presence(activity=discord.Game(name="بحرس زعامة أبو عيسى وعجيب 👑"))

        @client.event
        async def on_message(message):
            if message.author == client.user: return
            if is_bsf_message(message.content):
                await message.channel.send(RESPONSE_TEXT)

        token = os.getenv('DISCORD_TOKEN')
        if not token:
            print("⚠️ DISCORD_TOKEN مش موجود - رح اكمل تيليجرام لحاله")
            return
        
        await client.start(token)
    except Exception as e:
        print(f"❌ Discord Error: {e}")

async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and is_bsf_message(update.message.text):
        await update.message.reply_text(RESPONSE_TEXT)

async def run_telegram():
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            print("⚠️ TELEGRAM_TOKEN مش موجود - رح اكمل ديسكورد لحاله")
            return

        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))
        print('✅ TELEGRAM LIVE')
        await app.run_polling() # هاي بتغنيك عن Event().wait
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

async def main():
    print("🔥 BSF BOT STARTING... بزعامة عجيب وابو عيسى")
    await asyncio.gather(run_discord(), run_telegram())

if __name__ == '__main__':
    asyncio.run(main())
