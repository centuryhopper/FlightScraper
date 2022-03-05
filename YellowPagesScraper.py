#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from time import strftime

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'www.yellowpages.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
            }



html = requests.get('https://www.yellowpages.com/search?search_terms=restaurant&geo_location_terms=Orlando',headers=headers)
# html.status_code



bsobj = soup(html.content,'html.parser')
# bsobj



resturant_name = []
for names in bsobj.findAll('div',{'class':'search-results organic'}):
    for name in names.findAll('a',{'class':'business-name'}):
        resturant_name.append(name.span.text.strip())

# resturant_name



phone_number = []
for number in bsobj.findAll('div',{'class':'phones phone primary'}):
    phone_number.append(number.text.strip())


# phone_number


address = []
for adr in bsobj.findAll('div',{'class':'info-section info-secondary'})[1:]:
    street = adr.findAll('div',{'class':'street-address'})[0].text
    locality = adr.findAll('div',{'class':'locality'})[0].text
    address.append(street+locality)
# address



website = []
for link in bsobj.findAll('a',{'class':'track-visit-website'}):
    website.append(link['href'])

# website

d = {'resturant_name': resturant_name, 'phone_number': phone_number, 'address':address, 'website':website}

df = pd.DataFrame.from_dict(d, orient='index')
df = df.transpose()

df.to_csv(f'./YelloPagesData/data_{strftime("%Y%m%d-%H%M%S")}.csv')





