#!/usr/bin/env python3
"""
Extract additional information from wiki.contextgarden.net
"""
import re
import sys
import json
import cson
import requests
from pathlib import Path
from pprint import pprint
from bs4 import BeautifulSoup

infofile = Path('tools/context-infos.cson')
#infofile2 = Path('tools/context-infos2.cson')

print(f'reading {infofile}')

with open(infofile, 'r') as info:
    data = cson.load(info)

# TODO: save backup?

def find_in_soup(soup, class_):
    found = soup.find(class_=class_)
    try:
        return ' '.join(found.stripped_strings)
    except:
        return ''

for cmd in data:
    entry = data[cmd]
    text = ''
    desc = entry['description'] + ' '
    text = desc
    print('{}: {}'.format(cmd, desc))

    r = requests.get(entry['url'])
    #pprint(r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    if find_in_soup(soup, "noarticletext"):
        # page doesn’t exist
        data[cmd]['url'] = ''
    short = find_in_soup(soup, "cd:shortdesc")
    long = find_in_soup(soup, "cd:description")
    # try to avoid doubling:
    if (desc in short) or (desc in long):
        text = ''
    if not ((short in desc) or (short in long)):
        text += short + ' '
    text += long
    print(text+'\n')
    data[cmd]['description'] = text.strip()

with open(infofile, 'w') as info:
    cson.dump(data, info, ensure_ascii=False, indent=2)
