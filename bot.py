import os
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🔥 البوت العجيب شغال! زعامة عجيب وابو عيسى BSF 👑")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    txt = m.text.lower()
    name = m.from_user.first_name
    if "عجيب" in txt:
        bot.reply_to(m, f"👑 الزعيم عجيب تاج الراس! هلا يا {name} 🔥")
    elif "ابو عيسى" in txt:
        bot.reply_to(m, f"🦅 الزعيم ابو عيسى الأسطورة! هلا يا {name} 👑")
    elif "bsf" in txt:
        bot.reply_to(m, f"🔥 BSF عيلة ما بتنهز! يا {name} 💪")
    else:
        bot.reply_to(m, f"هلا يا {name} 😎 اكتب BSF او عجيب")

bot.infinity_polling()
