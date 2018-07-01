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
    
    Bedeutung der Emojis:
    Vegane Speise:🌱👌
    Ohne Fleisch:🌱
    Mit Fisch bzw. Meeresfrüchten:🐟
    Mit Geflügel:🐣
    Mit Schweinefleisch:🐷
    Mit Rindfleisch:🐄
    
    Folgende Inhaltsstoffe werden berücksichtigt:
    11:🥃 (Alkohol)
    20[a-f]:🌾 (Gluten aus verschiedenen Quellen)
    24:🥜 (Erdnüsse)
    25:[Soja]
    26:🥛 (Milch)
    27[a-g]:🌰 (verschiedene Nüsse, aber keine Erdnüsse)
    
    Kurzes Menü:
    +3x🍛: dazu drei Beilagen
    🥗🍮: dazu Salat und Desert
    🥗: dazu Salat

    
    Bug reports und Verbesserungsvorschläge bitte an @elayn"""
    # `/grillstation` — Zeigt das Menü der Grillstation an
    # `/beilagen` — Zeigt an, welche Beilagen es im Moment gibt
    bot.sendMessage(chat_id = update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)


dispatcher.add_handler(tex.CommandHandler('help', help))

def send_error_msg(bot,update,message="Ich kann kein Menü für heute finden."):
    if type(update) == int:
        chat_id = update
    else:
        chat_id = update.message.chat_id

    bot.sendMessage(chat_id = chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)
    bot.send_photo(chat_id = chat_id, photo = open('images/archives.jpg', 'rb'))
dispatcher.add_handler(tex.CommandHandler('error', send_error_msg))


def menu(bot, update):
    if latest_menu is None:
        send_error_msg(bot,update,"Ich kann kein Menü für heute finden.")
        return

    menu = ""
    menu += "Menü für " + latest_menu["Datum"] + "\n\n"
    for i in latest_menu["Menu"]:
        tag_line = ""
        for tag in i.tags:
            tag_line += tag if tag != "Kinderteller" else ""
        menu += tag_line + i.allergens() + " | " + i.beautiful_description() + ", " + i.price + "\n"

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
        menu += i.short_description() + "\n"

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

    latest_menu = None
    try:
        latest_menu = scrap()
    except:
        print("Couldn't fetch menu: ", sys.exc_info()[0])
        # updater.job_queue.run_once(fetch_menu, 5)
        return

    try:
        pickle.dump(latest_menu, open("menus/" + time.strftime("%m-%d-%Y") + ".pickle", "wb"))
    except:
        print("Couldn't pickle menu to disk!")
        pass # this is not important enough to crash the bot

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


def how_hot_am_i(bot,update):
    chat_id = update.message.chat_id
    bot.send_chat_action(chat_id = chat_id, action = telegram.ChatAction.TYPING)
    time.sleep(2)
    bot.send_photo(chat_id = chat_id, photo = open('images/pretty-basic-1.png', 'rb'))
    bot.send_chat_action(chat_id = chat_id, action = telegram.ChatAction.TYPING)
    time.sleep(5)
    bot.send_photo(chat_id = chat_id, photo = open('images/pretty-basic-2.png', 'rb'))
dispatcher.add_handler(tex.CommandHandler('how_hot_am_i', how_hot_am_i))



updater.job_queue.run_daily(fetch_and_send_menu, datetime.time(11, 00))
# updater.job_queue.run_repeating(fetch_and_send_menu,10)

fetch_menu()
print("Bot active.")
updater.start_polling()
