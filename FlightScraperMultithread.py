import os
import re
import sys
from random import randint
import concurrent.futures
from time import sleep, strftime

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities
from fake_useragent import FakeUserAgentError, UserAgent


# working one: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423Fv

os.chdir(os.path.dirname(__file__))

# chrome_options = Options()
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument('--disable-blink-features=AutomationControlled')
# chrome_options.add_argument("--headless")
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# lastDate = ''
# if not os.path.isfile(f'{os.getcwd()}/time_stamp.txt'):
#     print('creating file')
#     with open(f'{os.getcwd()}/time_stamp.txt', 'w') as f:
#         f.write('')
# with open(f'{os.getcwd()}/time_stamp.txt', 'r') as f:
#     lastDate = f.read()
#     if lastDate == strftime("%Y-%m-%d"):
#         print('already ran this')
#         driver.quit()
#         sys.exit()
# with open(f'{os.getcwd()}/time_stamp.txt', 'w') as f:
#     f.write(strftime("%Y-%m-%d"))


def load_more(webDriver):
    '''Load more results to maximize the scraping'''
    try:
        more_results = '//a[@class = "moreButton"]'
        # driver.find_element_by_xpath(more_results).click()
        webDriver.find_element(By.XPATH, more_results).click()
        print('loading more results...')
        sleep(randint(10, 15))
    except:
        pass

def threadWork(anchorTagDataCode, flightCategory):
    city_from = os.getenv('startCity')
    city_to = os.getenv('destinationCity')
    date_start = '2022-07-05'
    date_end = '2022-08-24'
    kayakLink = 'https://www.kayak.com/flights/' + city_from + '-' + city_to + \
        '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a'
    PROXY = "23.23.23.23:3128"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # chrome_options.add_argument(f'user-agent={UserAgent().chrome}')
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    # chrome_options.add_argument(f"--window-size={randint(480,1920)},{randint(480,1080)}")
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')

    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True
    webDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options, desired_capabilities=capabilities)
    webDriver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": UserAgent().random})
    webDriver.get(kayakLink)
    # webDriver.maximize_window()
    webDriver.implicitly_wait(randint(15, 20))

    # sometimes a popup shows up, so we can use a try statement to check it and close
    try:
        xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]'
        webDriver.find_elements(By.XPATH, xp_popup_close)[5].click()
    except Exception as e:
        pass

    sleep(randint(5, 10))

    # with open(f'{flightCategory}.txt', 'w') as f:
    #     f.write(webDriver.page_source)

    results = f'//a[@data-code = "{anchorTagDataCode}"]'
    # results_button = webDriver.find_element(By.XPATH, results)
    results_button = WebDriverWait(webDriver, 10).until(EC.presence_of_element_located((By.XPATH, results)))
    webDriver.execute_script("arguments[0].click();", results_button)
    load_more(webDriver)
    webDriver.save_screenshot(f'{os.getcwd()}/pics/{flightCategory}.png')
    df = page_scrape(webDriver)
    df['sort'] = flightCategory
    webDriver.quit()
    # print(df)
    return df

def page_scrape(driver):
    """This function takes care of the scraping part"""

    xp_sections = '//*[@class="section duration allow-multi-modal-icons"]'
    # sections = driver.find_elements_by_xpath(xp_sections)
    sections = driver.find_elements(By.XPATH, xp_sections)

    sections_list = [value.text if value else '' for value in sections]
    # from a to b
    section_a_list = sections_list[::2]  # This is to separate the two flights
    # from b back to a
    section_b_list = sections_list[1::2]  # This is to separate the two flights

    # if you run into a reCaptcha, you might want to do something about it
    # you will know there's a problem if the lists above are empty
    # this if statement lets you exit the bot or do something else
    # you can add a sleep here, to let you solve the captcha and continue scraping
    # i'm using a SystemExit because i want to test everything from the start
    if section_a_list == []:
        sleep(60)

    # I'll use the letter A for the outbound flight and B for the inbound
    out_duration = []
    out_section_cities = []
    for n in section_a_list:
        # Separate the time from the cities
        if n:
            out_section_cities.append(''.join(n.split()[2:5]))
            out_duration.append(''.join(n.split()[0:2]))

    # print(f'before {out_duration = }')

    # filter out all times that are more than 9 hours
    out_duration = list(filter(lambda duration: int(''.join(re.findall('\d', duration))) <= 900, out_duration))

    # print(f'after {out_duration = }')

    return_duration = []
    return_section_cities = []
    for n in section_b_list:
        # Separate the time from the cities
        if n:
            return_section_cities.append(''.join(n.split()[2:5]))
            return_duration.append(''.join(n.split()[0:2]))

    # print(f'before {return_duration = }')

    return_duration = list(filter(lambda duration: int(''.join(re.findall('\d', duration))) <= 900, return_duration))

    # print(f'after {return_duration = }')



    xp_dates = '//div[@class="section date"]'
    # dates = driver.find_elements_by_xpath(xp_dates)
    dates = driver.find_elements(By.XPATH, xp_dates)
    dates_list = [value.text for value in dates]
    a_date_list = dates_list[::2]
    b_date_list = dates_list[1::2]
    # Separating the weekday from the day
    a_day = [value.split()[0] for value in a_date_list if len(value.split()) > 0]
    a_weekday = [value.split()[1] for value in a_date_list if len(value.split()) > 1]
    b_day = [value.split()[0] for value in b_date_list if len(value.split()) > 0]
    b_weekday = [value.split()[1] for value in b_date_list if len(value.split()) > 1]
    # return None

    # getting the prices
    xp_prices = '//span[@class="price option-text"]'
    # prices = driver.find_elements_by_xpath(xp_prices)
    # prices = driver.find_elements(By.XPATH, xp_prices)
    prices = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, xp_prices)))

    prices_list = [int(price.text.replace('$', ''))
                   for price in prices if price.text != '' and price.text.replace('$', '').isdigit()]
    # prices_list = list(map(int, prices_list))


    # the stops are a big list with one leg on the even index and second leg on odd index
    # What is this snippet doing ?? ~Leo
    xp_stops = '//div[@class="section stops"]/div[1]'
    # stops = driver.find_elements_by_xpath(xp_stops)
    # stops = driver.find_elements(By.XPATH, xp_stops)
    stops = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, xp_stops)))
    try:
        stops_list = [stop.text[0].replace('n', '0') if stop and stop.text else '' for stop in stops ]
    except Exception as e:
        for stop in stops:
            print(stop.text)
        pass
    a_stop_list = stops_list[::2]
    b_stop_list = stops_list[1::2]

    xp_stops_cities = '//div[@class="section stops"]/div[2]'
    # stops_cities = driver.find_elements_by_xpath(xp_stops_cities)
    # stops_cities = driver.find_elements(By.XPATH, xp_stops_cities)
    stops_cities = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, xp_stops_cities)))
    stops_cities_list = [stop.text for stop in stops_cities if stop]
    a_stop_name_list = stops_cities_list[::2]
    b_stop_name_list = stops_cities_list[1::2]


    # this part gets me the airline company and the departure and arrival times, for both legs
    xp_schedule = '//div[@class="section times"]'
    # schedules = driver.find_elements_by_xpath(xp_schedule)
    # schedules = driver.find_elements(By.XPATH, xp_schedule)
    schedules = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, xp_schedule)))
    hours_list = []
    carrier_list = []
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0] if schedule and schedule.text else '')
        carrier_list.append(schedule.text.split('\n')[1] if schedule and schedule.text else '')

    # split the hours and carriers, between a and b legs
    a_hours = hours_list[::2]
    a_carrier = carrier_list[::2]
    b_hours = hours_list[1::2]
    b_carrier = carrier_list[1::2]

    flights_df = pd.DataFrame.from_dict({'Out Day': a_day,
                                         'Out Weekday': a_weekday,
                                         'Out Duration': out_duration,
                                         'Out Cities': out_section_cities,
                                         'Return Day': b_day,
                                         'Return Weekday': b_weekday,
                                         'Return Duration': return_duration,
                                         'Return Cities': return_section_cities,
                                         'Out Stops': a_stop_list,
                                         'Out Stop Cities': a_stop_name_list,
                                         'Return Stops': b_stop_list,
                                         'Return Stop Cities': b_stop_name_list,
                                         'Out Time': a_hours,
                                         'Out Airline': a_carrier,
                                         'Return Time': b_hours,
                                         'Return Airline': b_carrier,
                                         'Price': prices_list}, orient='index')
    # rows become columns
    flights_df = flights_df.transpose()

    # so we can know when it was scraped
    flights_df['timestamp'] = strftime("%Y%m%d-%H%M")
    return flights_df

def main():
    # city_from = input('From which city? ')
    # city_to = input('Where to? ')
    # date_start = input('Search around which departure date? Please use YYYY-MM-DD format only ')
    # date_end = input('Return when? Please use YYYY-MM-DD format only ')
    city_from = os.getenv('startCity')
    city_to = os.getenv('destinationCity')
    date_start = '2022-07-05'
    date_end = '2022-07-10'

    codes = ['bestflight', 'price', 'duration']
    cats = ['best','cheap','quick']

    ans = None
    # multi-threading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = executor.map(threadWork,codes,cats)
        # list of dataframes
        ans = list(res)

    # print(type(ans[0]))
    # print('done')

    # saving a new dataframe as an excel file. the name is custom made to your cities and dates
    final_df = pd.concat(ans)
    currentTime = strftime("%Y%m%d-%H%M%S")
    fileName = '{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(currentTime, city_from, city_to, date_start,date_end)
    if not os.path.exists(os.getcwd() + '/_FlightPrices/'):
        os.mkdir(os.getcwd() + '/_FlightPrices/')
    filePathComplete = os.getcwd() + '/_FlightPrices/' + fileName
    final_df.to_excel(filePathComplete, index=False)

    return final_df


#region old code
    # for n in range(0,5):
    #     start_kayak(city_from, city_to, date_start, date_end)
    #     print('iteration {} was complete @ {}'.format(n, strftime("%Y%m%d-%H%M")))

    #     # Wait 4 hours
    #     sleep(60*60*4)
    #     print('sleep finished.....')

#endregion




if __name__ == '__main__':
    # main()
    df = main()
    print(df)
    print('Kayak plane ticket price scraping complete!')
