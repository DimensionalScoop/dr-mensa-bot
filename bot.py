import telegram
import logging
import telegram.ext as tex
import helpers
from scrapper import scrap

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = tex.Updater(input("Token plx owo"))
dispatcher = updater.dispatcher
bot = updater.bot
subscribers = []

print("Started Dr. Mensa Bot:", bot.getMe())

# Handler functions
def start(bot, update):
    message = "Der *Drop-in replacement (Dr.) Mensa Bot* liefert nun jeden pünklich Tag das Menü."
    subscribers.append(update.message.chat_id)
    bot.sendMessage(chat_id=update.message.chat_id, text=message,parse_mode=telegram.ParseMode.MARKDOWN)

def help(bot, update):
    message = """Commands:
    (c) by Max Pernklau."""
    bot.sendMessage(chat_id=update.message.chat_id, text=message)

def menu(bot,update):
    menu = ""
    for i in latest_menu["Menu"]:
        tag_line = ""
        for tag in i.tags:
            tag_line += tag if tag!= "Kinderteller" else ""
        menu += tag_line + " " + i.beautiful_description() + ", " + i.price + "\n"

    menu = helpers.emojify(menu)
    print(menu)
    bot.sendMessage(chat_id = update.message.chat_id, text = menu, parse_mode = telegram.ParseMode.MARKDOWN)

def short_menu(bot,update):
    menu = ""
    for i in latest_menu["Menu"]:
        tag_line = ""
        for tag in i.tags:
            tag_line += tag if tag!= "Kinderteller" else ""
        menu += i.beautiful_description() + "\n"

    menu = helpers.completely_emojify(menu)
    print(menu)
    bot.sendMessage(chat_id = update.message.chat_id, text = menu, parse_mode = telegram.ParseMode.MARKDOWN)

latest_menu = None
def fetch_menu():
    global latest_menu
    print("Fetching Menu")
    latest_menu = scrap()


dispatcher.add_handler(tex.CommandHandler('start', start))
dispatcher.add_handler(tex.CommandHandler('help', help))
dispatcher.add_handler(tex.CommandHandler('menu', menu))
dispatcher.add_handler(tex.CommandHandler('short_menu', short_menu))

fetch_menu()

print("Waiting for clients")
updater.start_polling()
