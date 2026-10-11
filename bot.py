import discord
from discord.ext import commands
import os
import threading
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ دود + بهارات - بهارتك يا موشي شغال!"

@app.route('/baharat')
def baharat_game():
    try:
        return send_file('baharat_game.html')
    except Exception as e:
        return f"خطأ: {e} - تأكد ان الملف موجود", 500

# --- Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def بهارت(ctx):
    await ctx.send("بهارتك يا موشي! 🧂 العب: https://amazing-bot-k92g.onrender.com/baharat")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        app.run(host="0.0.0.0", port=10000)
