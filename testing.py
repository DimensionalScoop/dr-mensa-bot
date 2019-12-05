from helpers import *
import pickle
import sys
import scrapper

result = scrapper.scrap()

sys.exit()
menu = pickle.load(open("menus/07-01-2018.pickle", "rb"))["Menu"]
print(menu)
print(pickle.load(open("menus/07-01-2018.pickle", "rb"))["FullMenu"])
for i in menu:
    print(i.allergens())
