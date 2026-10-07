import os
import telebot
import random
from phrases import BSF_PHRASES, WELCOME_MSG

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    name = m.from_user.first_name
    bot.reply_to(m, WELCOME_MSG.format(name=name))

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    txt = m.text.lower()
    name = m.from_user.first_name
    
    if "عجيب" in txt or "ابو عيسى" in txt or "bsf" in txt.lower():
        phrase = random.choice(BSF_PHRASES)
        bot.reply_to(m, f"{phrase}\nهلا يا {name} 👑")
    else:
        bot.reply_to(m, f"هلا يا {name} 😎 اكتب BSF او عجيب او ابو عيسى وشوف الزعامة!")

bot.infinity_polling()
