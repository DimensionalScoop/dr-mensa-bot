import re

def emojify_allergens(tags):
    result = ""
    tag_string = "".join(tags)

    rules = {"24":"🥜","20[a-f]":"🌾","11":"🥃","25":"[Soja]","26":"🥛","27[a-g]":'🌰'}

    for r in rules:
        if re.search(r,tag_string):
            result += rules[r]

    return result



def emojify(string):
    rules = {"Vegane Speise":"🌱👌","Kinderteller":"🧒","Mit Fisch bzw. Meeresfrüchten":"🐟", "Mit Geflügel":"🐣", "Ohne Fleisch":"🌱", "Knoblauch":"Knofi 👌👌", "Mit Schweinefleisch":'🐷',"Mit Rindfleisch":'🐄'}
    for key in rules:
        string = re.sub(key,rules[key],string)
    return string

def shorten_emojify(string):
    string = emojify(string)
    rules_priority = {"(?:, )?dazu eine Salatschale":'🥗',"(?:, )?dazu drei beilagen":'+3x🍛',"(?:, )?dazu Salat und Dessert":'🥗🍮'}
    rules = {"salat":'🥗',"dessert":'🍮',"griechisch":'🇬🇷'," & drei Beilagen":' +3x🍛',"(?:, )und":' &',"und":'&', "dazu":'&', "(?:, )dazu":' &',"mit":"w/"}
    for key in rules_priority:
        string = re.sub(key, rules_priority[key], string, flags=re.IGNORECASE)
    for key in rules:
        string = re.sub(key, rules[key], string, flags=re.IGNORECASE)
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
        removed_tags = re.sub("\([0-9abcdefg,]*\)", '', self.description)  # removes tags like "(1a)","(15,18,20b)"
        beautify = re.sub("\s?,\s?", ", ", removed_tags)
        beautify = re.sub("\sDip", "-Dip", beautify)
        beautify = re.sub(",? dazu 3 Beilagen nach Wahl", " & drei Beilagen",beautify)
        beautify = re.sub("Madras", "Thea-S.-Gedächtnis-Madras🍢", beautify)
        beautify = re.sub("\s\s", " ", beautify)
        # beautify = re.sub(".?$",".",beautify)
        return beautify.strip()

    def short_description(self):
        desc = self.beautiful_description()
        strip = ["mit soße","mit sauce","vom grill","mit kräuterbutter","\(Knoblauch\)"]
        comma_strip = "(?:, )?"
        for rule in strip:
            desc = re.sub(comma_strip+rule+comma_strip,"",desc,flags=re.IGNORECASE)

        return shorten_emojify(desc)


    def allergens(self):
        found_allergens = []
        allergen_groups = re.findall("\(([0-9abcdefg,]*)\)", self.description)
        for g in allergen_groups:
            found_allergens.extend(re.findall("(\d+[a-g]?)",g))
        return emojify_allergens(found_allergens)

    def tags_as_emoji(self):
        tags = []
        for i in self.tags:
            tags.append(emojify(i))
        return tags