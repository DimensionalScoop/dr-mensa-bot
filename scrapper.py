from urllib.request import urlopen
from bs4 import BeautifulSoup
import bs4
import re
from helpers import *
import ssl


def scrap():
    results = {}

    url = "https://www.stwdo.de/mensa-co/tu-dortmund/hauptmensa/"
    # for testing purposes
    # url = "https://www.stwdo.de/mensa-co/tu-dortmund/hauptmensa/?tx_pamensa_mensa%5Baction%5D=day&tx_pamensa_mensa%5Bcontroller%5D=OnlinePlan&cHash=d69c17785f24fe4043453debb1687c81"
    ssl._create_default_https_context = ssl._create_unverified_context
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")

    # Öffnungszeiten
    try:
        box = soup.find("span", attrs={"id": "timer--inner-1"})
        text = box.text.strip()
        search_result = re.search(r"((\d.*\d))", text)
        results["Öffnungszeiten"] = search_result.group(0).lower()
    except AttributeError:
        results["Öffnungszeiten"] = "Geschlossen"

    # Datum
    box = soup.find(name="div", attrs={"class": "meals-wrapper"}).find(name="h2")
    text = box.text.strip()
    results["Datum"] = re.search(r"(\w*, \d\d.*)", text).group(0)

    # Menü
    menu = soup.find("div", attrs={"class": "meals-body"})
    gerichte = []
    for i in menu.children:
        if type(i) == bs4.element.Tag:
            if i.find("div", attrs={"class": "item description"}):
                tag = i.find_all("div", attrs={"class": re.compile("item category")})
                tag = tag[0].find("img")
                category = tag.attrs["alt"]
                desc = i.find("div", attrs={"class": "item description"}).text.strip()
                price = i.find(
                    "div", attrs={"class": "item price student"}
                ).text.strip()
                tags = list(
                    [
                        k.attrs["alt"]
                        for k in i.find(
                            "div", attrs={"class": "item supplies"}
                        ).findAll("img")
                    ]
                )
                gerichte.append(Gericht(category, desc, tags, price))

    results["FullMenu"] = gerichte
    results["Menu"] = list(
        [
            i
            for i in gerichte
            if (
                i.category == "Tagesgericht"
                or i.category == "Menü 1"
                or i.category == "Menü 2"
                or i.category == "Vegetarisches Menü"
                or i.category == "Aktionsteller Fisch"
                or i.category == "Aktionsteller Vegan"
                or i.category == "Aktionsteller"
            )
        ]
    )

    return results
