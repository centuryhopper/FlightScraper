# #!/usr/bin/env python
# # coding: utf-8


# DOESNT WORk

# import time
# import requests
# from time import sleep
# from bs4 import BeautifulSoup as soup
# import pandas as pd
# import re
# import os
# import sys

# os.chdir(os.path.dirname(__file__))


# from fake_useragent import UserAgent, FakeUserAgentError
# ua = None
# while True:
#     try:
#         ua = UserAgent()
#         break
#     except FakeUserAgentError:
#         print('fake user agent error')
#         continue
#     except Exception:
#         continue

# fake_agent = ua.random
# print(fake_agent)

# HEADERS = {"User-Agent": fake_agent, 'Accept-Language': 'en-US, en;q=0.5'}

# city_state = "Orlando_Florida"
# html = requests.get(f'https://www.tripadvisor.in/Restaurants-g34515-{city_state}.html', headers=HEADERS, timeout=5)

# bsobj = soup(html.content,'html.parser')
# # print(bsobj.contents)

# restaurants = []
# urls = []
# for name in bsobj.findAll('a',{'class':'oHGMl'}):
#     restaurants.append(name.text.strip())
#     urls.append(f"https://www.tripadvisor.in{name['href']}")

# ratings = []
# reviews = []
# for o in bsobj.findAll('div',{'class':'jVDab o W f u w JqMhy'}):
#     toParse = o.get('aria-label')
#     print(toParse)
#     if toParse:
#         match = re.search('(.*bubbles)\.\s(.*)', toParse, re.IGNORECASE)
#         ratings.append(match.group(1))
#         reviews.append(match.group(2))

# description = []

# for p in bsobj.findAll('span',{'class':'hCoKk o W q'}):
#     description.append(p.text.strip())


# d1 = {'Restaurant': restaurants, 'URL': urls, 'Ratings': ratings, 'No_of_Reviews': reviews, 'description': description}
# for k,v in d1.items():
#     print(k, len(v))
# df = pd.DataFrame.from_dict(d1, orient='index')
# df = df.transpose()
# # print(df)

# RestaurantsFolderPath = os.getcwd() + "/Scraped_Restaurants_Data/"
# if not os.path.exists(RestaurantsFolderPath):
#     os.makedirs(RestaurantsFolderPath)

# df.to_csv(f'{RestaurantsFolderPath}Orlando_Florida_{time.strftime("%Y%m%d-%H%M%S")}.csv')


