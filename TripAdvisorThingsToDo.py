#!/usr/bin/env python
# coding: utf-8

import time
import requests
from time import sleep
from bs4 import BeautifulSoup as soup
import pandas as pd
import re
import os
import sys

os.chdir(os.path.dirname(__file__))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", 'Accept-Language': 'en-US, en;q=0.5'}

city_state = "Orlando_Florida"
html = requests.get(f'https://www.tripadvisor.in/Attractions-g34515-{city_state}.html', headers=HEADERS, timeout=5)

bsobj = soup(html.content,'html.parser')

attractions = []
for name in bsobj.findAll('div',{'class':'keSJi FGwzt ukgoS'}):
    attractions.append(name.text.strip())

urls = []

for div in bsobj.findAll('div',{'class': '_T Cj'}):
    href = div.find('a',{'href' : re.compile('.*?html$')})
    # print(href['href'])
    urls.append(f"https://www.tripadvisor.in{href['href']}")

# https://www.tripadvisor.in


ratings = []
reviews = []
for o in bsobj.findAll('div',{'class':'jVDab o W f u w JqMhy'}):
    toParse = o.get('aria-label')
    print(toParse)
    if toParse:
        match = re.search('(.*bubbles)\.\s(.*)', toParse, re.IGNORECASE)
        ratings.append(match.group(1))
        reviews.append(match.group(2))

price = []

for p in bsobj.findAll('div',{'class':'biGQs _P fiohW avBIb fOtGX'}):
    price.append(p.text.replace('$','').strip())


d1 = {'attraction_name': attractions, 'URL': urls, 'Ratings': ratings, 'No_of_Reviews': reviews, 'Price': price}
for k,v in d1.items():
    print(k, len(v))
df = pd.DataFrame.from_dict(d1, orient='index')
df = df.transpose()
# print(df)

ThingsToDoFolderPath = os.getcwd() + "/Scraped_ThingsToDo_Data/"
if not os.path.exists(ThingsToDoFolderPath):
    os.makedirs(ThingsToDoFolderPath)

df.to_csv(f'{ThingsToDoFolderPath}Orlando_Florida_{time.strftime("%Y%m%d-%H%M%S")}.csv')


