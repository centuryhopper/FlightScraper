#!/usr/bin/env python
# coding: utf-8

import requests
from time import sleep
from bs4 import BeautifulSoup as soup



HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", 'Accept-Language': 'en-US, en;q=0.5'}
html = requests.get('https://www.tripadvisor.in/Hotels-g187147-Paris_Ile_de_France-Hotels.html', headers=HEADERS)
# html.status_code


bsobj = soup(html.content,'html.parser')


hotel = []
for name in bsobj.findAll('div',{'class':'listing_title'}):
    hotel.append(name.text.strip())


# hotel


ratings = []
for rating in bsobj.findAll('a',{'class':'ui_bubble_rating'}):
    ratings.append(rating['alt'])

# ratings



reviews = []

for review in bsobj.findAll('a',{'class':'review_count'}):
    reviews.append(review.text.strip())

# reviews


price = []

for p in bsobj.findAll('div',{'class':'price-wrap'}):
    price.append(p.text.replace('$','').strip())


# price[:5]


# len(price)


d1 = {'Hotel':hotel,'Ratings':ratings,'No_of_Reviews':reviews,'Price':price}


import pandas as pd


df = pd.DataFrame.from_dict(d1)
# df











