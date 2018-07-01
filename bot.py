import time

import telegram
import logging
import telegram.ext as tex
import helpers
from scrapper import scrap
import datetime
import pickle
import sys

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)

updater = tex.Updater(input("Token plx owo"))
dispatcher = updater.dispatcher
bot = updater.bot
try:
    subscribers = pickle.load(open("subscribers.pickle", "rb"))
    print("Loaded", len(subscribers), "subscribers from file.")
except:
    print("Didn't load subscribers from file!")
    subscribers = []

print("Started Dr. Mensa Bot:", bot.getMe())


# Handler functions
def start(bot, update):
    message = "Dies ist der _Drop-in replacement (Dr.) Mensa Bot_!"
    bot.sendMessage(chat_id = update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)
    help(bot, update)


dispatcher.add_handler(tex.CommandHandler('start', start))


def subscribe(bot, update):
    message = "Ihr bekommt ab jetzt jeden Tag um 11 Uhr das Mensa-Menü automatisch zugeschickt!"
    subscribers.append(update.message.chat_id)
    pickle.dump(subscribers, open("subscribers.pickle", "wb"))
    bot.sendMessage(chat_id = update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('subscribe', subscribe))


def unsubscribe(bot, update):
    message = "Ihr bekommt ab jetzt nichts mehr automatisch zugeschickt!"
    subscribers.remove(update.message.chat_id)
    pickle.dump(subscribers, open("subscribers.pickle", "wb"))
    bot.sendMessage(chat_id = update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('unsubscribe', unsubscribe))


def help(bot, update):
    message = """Commands:
    `/menu` — Zeigt das aktuelle Menü an
    `/short_menu` — Zeigt das aktuelle Menü in Kurzfassung an
    `/subscribe` — Das Menü wird jeden Werktag um 11 Uhr automatisch gepostet
    `/unsubscribe` — Deaktiviert das automatische Posten des Menüs
    Bug reports und Verbesserungsvorschläge bitte an @elayn
    (c) by Max Pernklau."""
    # `/grillstation` — Zeigt das Menü der Grillstation an
    # `/beilagen` — Zeigt an, welche Beilagen es im Moment gibt
    bot.sendMessage(chat_id = update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('help', help))


def menu(bot, update):
    menu = ""
    menu += "Menü für " + latest_menu["Datum"] + "\n\n"
    for i in latest_menu["Menu"]:
        tag_line = ""
        for tag in i.tags:
            tag_line += tag if tag != "Kinderteller" else ""
        menu += tag_line + " " + i.beautiful_description() + ", " + i.price + "\n"

    menu = helpers.emojify(menu)
    if type(update) == int:
        chat_id = update
    else:
        chat_id = update.message.chat_id
    bot.sendMessage(chat_id = chat_id, text = menu, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('menu', menu))


def short_menu(bot, update):
    menu = ""
    for i in latest_menu["Menu"]:
        tag_line = ""
        for tag in i.tags:
            tag_line += tag if tag != "Kinderteller" else ""
        menu += i.beautiful_description() + "\n"

    menu = helpers.completely_emojify(menu)

    if type(update) == str:
        chat_id = update
    else:
        chat_id = update.message.chat_id
    bot.sendMessage(chat_id = chat_id, text = menu, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('short_menu', short_menu))

latest_menu = None


def fetch_menu(bot = None, job = None, callback = None):
    print("Fetching menu...")
    global latest_menu
    try:
        latest_menu = scrap()
    except:
        print("Couldn't fetch menu: ", sys.exc_info()[0])
        latest_menu = None
        updater.job_queue.run_once(fetch_menu, 5)
        return

    pickle.dump(latest_menu, open("menus/" + time.strftime("%m-%d-%Y") + ".pickle", "wb"))

    if callback is not None:
        callback()


def fetch_and_send_menu(bot, job):
    if datetime.datetime.today().weekday() >= 5:  # it's Saturday or Sunday
        print("No menu on weekends.")
        return
    fetch_menu(callback = send_menu_to_subscribers)


def send_menu_to_subscribers():
    print("Sending menu to", len(subscribers), "subscribers.")
    for s in subscribers:
        menu(bot, s)


updater.job_queue.run_daily(fetch_and_send_menu, datetime.time(11, 00))
# updater.job_queue.run_repeating(fetch_and_send_menu,10)

fetch_menu()
print("Bot active.")
updater.start_polling()
