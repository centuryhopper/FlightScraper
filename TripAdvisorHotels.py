#!/usr/bin/env python
# coding: utf-8

import time
import requests
from time import sleep
from bs4 import BeautifulSoup as soup
import pandas as pd
import re
import os

os.chdir(os.path.dirname(__file__))

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36", 'Accept-Language': 'en-US, en;q=0.5'}

city_state = "Orlando_Florida"
html = requests.get(f'https://www.tripadvisor.in/Hotels-g34515-{city_state}-Hotels.html', headers=HEADERS)


bsobj = soup(html.content,'html.parser')


hotel = []
for name in bsobj.findAll('div',{'class':'listing_title'}):
    hotel.append(name.text.strip())


urls = []

for div in bsobj.findAll('div',{'class': 'listing_title'}):
    href = div.find('a',{'href' : re.compile('.*?html$')})
    # print(href['href'])
    urls.append(f"https://www.tripadvisor.in{href['href']}")

# https://www.tripadvisor.in


ratings = []
for rating in bsobj.findAll('a',{'class':'ui_bubble_rating'}):
    ratings.append(rating['alt'])


reviews = []

for review in bsobj.findAll('a',{'class':'review_count'}):
    reviews.append(review.text.strip())


price = []

for p in bsobj.findAll('div',{'class':'price-wrap'}):
    price.append(p.text.replace('$','').strip())


d1 = {'Hotel': hotel, 'URL': urls, 'Ratings': ratings, 'No_of_Reviews': reviews, 'Price': price}
df = pd.DataFrame.from_dict(d1)
# print(df)

hotelFolderPath = os.getcwd() + "/Scraped_Hotel_Data/"
if not os.path.exists(hotelFolderPath):
    os.makedirs(hotelFolderPath)
df.to_csv(f'{hotelFolderPath}Orlando_Florida_{time.strftime("%Y%m%d-%H%M%S")}.csv')


