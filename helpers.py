import re


def emojify(string):
    rules = {"Vegane Speise":"🌱👌","Kinderteller":"🧒","Mit Fisch bzw. Meeresfrüchten":"🐟", "Mit Geflügel":"🐣", "Ohne Fleisch":"🌱", "Knoblauch":"Knofi 👌👌", "Mit Schweinefleisch":'🐷',"Mit Rindfleisch":'🐄'}
    for key in rules:
        string = re.sub(key,rules[key],string)
    return string

def completely_emojify(string):
    string = emojify(string).lower()
    rules = {"pute":"🍗","geschnetzeltes":"✂️","kokos":"🥥","limette":'🍋',"salat":'🥗',"dessert":'🍮',"griechisch":'🇬🇷',"drei beilagen":'+3x🍛',"fisch":'🐠',"käse":'🧀',"kartoffel":'🥔',"paris":'🇫🇷',"stangenbrot":'🥖',"und":'➕', "dazu":'➕',"faggottini pomodori":'🍜', "mit":"w/"}
    for key in rules:
        string = re.sub(key, rules[key], string)
    return string

class Gericht():
    def __init__(self, category, description, tags, price):
        self.price = re.search("([\d.,]*)\W?€", price).group(0)
        self.tags = tags
        self.description = description
        self.category = category

    def __repr__(self):
        return self.category

    def __str__(self):
        return self.beautiful_description() + "\t" + self.price + "\t" + str(self.tags_as_emoji())

    def beautiful_description(self):
        removed_tags = re.sub("\([0-9abcde,]*\)", '', self.description)  # removes tags like "(1a)","(15,18,20b)"
        beautify = re.sub("\s?,\s?", ", ", removed_tags)
        beautify = re.sub("\sDip", "-Dip", beautify)
        beautify = re.sub(",? dazu 3 Beilagen nach Wahl", " & drei Beilagen",beautify)
        beautify = re.sub("Madras", "Thea-S.-Gedächtnis-Madras", beautify)
        beautify = re.sub("\s\s", " ", beautify)
        # beautify = re.sub(".?$",".",beautify)
        return beautify.strip()

    def tags_as_emoji(self):
        tags = []
        for i in self.tags:
            tags.append(emojify(i))
        return tags