import requests
import json
import os
import string
from lxml import etree

SITE_ROOT = "http://magiccards.info"
SITE_MAP = "http://magiccards.info/sitemap.html"


def filename_encode(name):
    return ''.join([n for n in name if n in string.digits + string.letters])


def parse_sets(url):
    html = etree.HTML(requests.get(url).content)

    # Select the second table
    table = html.findall(".//table")[1]

    for header in table.findall(".//h3"):
        if header.text in ["Expansions", "Core Sets"]:
            ul = header.getnext()
            for a in ul.findall(".//a"):
                yield a.text, SITE_ROOT + a.attrib["href"]


def parse_cards(url):
    html = etree.HTML(requests.get(url).content)
    card_set, lang = html.findtext(".//small").split("/")
    tables = html.findall(".//table")
    table = tables[3]

    cards = []

    for tr in table.findall(".//tr")[1:]:
        no, name, ctype, mana, rarity, artist, edition = tr.findall(".//td")
        card_url = "{}/{}/{}/{}.html".format(
                SITE_ROOT, card_set, lang, no.text)
        image_url = "{}/scans/{}/{}/{}.jpg".format(
                SITE_ROOT, lang, card_set, no.text)
        cards.append({
            "number": int(no.text),
            "url": card_url,
            "image": image_url,
            "name": name.find("a").text,
            "type": ctype.text,
            "mana": mana.text,
            "rarity": rarity.text,
            "artist": artist.text,
            "edition": card_set,
            })

    return cards


if __name__ == "__main__":

    # Make sets directory
    os.mkdir("sets")

    for name, url in parse_sets(SITE_MAP):
        card_set = {
            "name": name,
            "url": url,
            "cards": parse_cards(url),
            }

        f = open("sets/{}.json".format(filename_encode(name)), "w")
        json.dump(card_set, f, sort_keys=True, indent=4)
        f.close()
