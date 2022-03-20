from time import sleep, strftime
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from secrets import Secrets
import pandas as pd

chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
sleep(2)


def load_more():
    '''Load more results to maximize the scraping'''
    try:
        more_results = '//a[@class = "moreButton"]'
        # driver.find_element_by_xpath(more_results).click()
        driver.find_element(By.XPATH, more_results).click()
        print('sleeping.....')
        # sleep(randint(25,35))
        sleep(randint(10, 15))
    except:
        pass

def start_kayak(city_from, city_to, date_start, date_end):
    """City codes - it's the IATA codes!
    Date format -  YYYY-MM-DD"""

    kayakLink = 'https://www.kayak.com/flights/' + city_from + '-' + city_to + \
        '/' + date_start + '-flexible/' + date_end + '-flexible?sort=bestflight_a'
    print(kayakLink)
    driver.get(kayakLink)
    driver.maximize_window()
    sleep(randint(8, 10))
    # sometimes a popup shows up, so we can use a try statement to check it and close
    try:
        xp_popup_close = '//button[contains(@id,"dialog-close") and contains(@class,"Button-No-Standard-Style close ")]'
        # driver.find_elements_by_xpath(xp_popup_close)[5].click()
        driver.find_elements(By.XPATH, xp_popup_close)[5].click()
    except Exception as e:
        pass
    # sleep(randint(60,95))
    sleep(randint(5, 10))
    print('loading more.....')
    load_more()
    print('starting first scrape.....')
    df_flights_best = page_scrape()
    df_flights_best['sort'] = 'best'
    # sleep(randint(60,80))
    sleep(randint(5, 10))

    # Let's also get the lowest prices from the matrix on top
    # matrix = driver.find_elements_by_xpath('//*[contains(@id,"FlexMatrixCell")]')
    # matrix = driver.find_elements(By.XPATH,'//*[contains(@id,"FlexMatrixCell")]')
    matrix = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@id,"FlexMatrixCell")]')))
    sleep(randint(5, 10))
    matrix_prices = [int(price.text.replace('$', ''))
                     for price in matrix if price.text if price.text.replace('$', '').isdigit()]
    matrix_min = min(matrix_prices)
    matrix_avg = sum(matrix_prices)/len(matrix_prices)

    print('switching to cheapest results.....')
    sleep(randint(3, 5))
    cheap_results = '//a[@data-code = "price"]'
    # cheap_results_button = driver.find_element_by_xpath(cheap_results)
    cheap_results_button = driver.find_element(By.XPATH, cheap_results)
    driver.execute_script("arguments[0].click();", cheap_results_button)
    # driver.find_element_by_xpath(cheap_results).click()
    sleep(randint(60, 90))
    print('loading more.....')

    load_more()

    print('starting second scrape.....')
    df_flights_cheap = page_scrape()
    df_flights_cheap['sort'] = 'cheap'
    # sleep(randint(60,80))
    sleep(randint(5, 10))

    print('switching to quickest results.....')
    quick_results = '//a[@data-code = "duration"]'
    # quick_results_button = driver.find_element_by_xpath(quick_results)
    quick_results_button = driver.find_element(By.XPATH, quick_results)
    driver.execute_script("arguments[0].click();", quick_results_button)
    sleep(randint(60, 90))
    print('loading more.....')

    load_more()

    print('starting third scrape.....')
    df_flights_fast = page_scrape()
    df_flights_fast['sort'] = 'fast'
    # sleep(randint(60,80))
    sleep(randint(5, 10))

    # saving a new dataframe as an excel file. the name is custom made to your cities and dates
    final_df = df_flights_cheap.append(df_flights_best).append(df_flights_fast)
    currentTime = strftime("%Y%m%d-%H%M")
    fileName = '{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(currentTime, city_from, city_to, date_start,date_end)
    filePathComplete = 'C:\\Users\\Leo Zhang\\Documents\\GitHub\\FlightScraper\\_FlightPrices\\{}'.format(fileName)
    final_df.to_excel(filePathComplete, index=False)


    # We can keep track of what they predict and how it actually turns out!
    xp_loading = '//div[contains(@class,"col-advice")]'
    # loading = driver.find_element_by_xpath(xp_loading).text
    loading = driver.find_element(By.XPATH, xp_loading).text
    xp_prediction = '//span[@class="info-text"]'
    # prediction = driver.find_element_by_xpath(xp_prediction).text
    prediction = driver.find_element(By.XPATH, xp_prediction).text
    print(loading+'\n'+prediction)

    # sometimes we get this string in the loading variable, which will conflict with the email we send later
    # just change it to "Not Sure" if it happens
    weird = '¯\\_(ツ)_/¯'
    if loading == weird:
        loading = 'N\\A'

    Secrets.sendEmail(filePathComplete, fileName, Secrets.EmailCredentials(sender=Secrets.senderEmail,
            password=Secrets.senderEmailPassword,
            recipients=Secrets.receiverEmails),
            subject='Kayak Flight Scraper Results',
            msg=f'Cheapest Flight: ${matrix_min}\nAverage Price: ${round(matrix_avg,2)}\nRecommendation: {loading}\n{prediction}\n\n---End of Message---',
            subtype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    print('saved df.....')
    # Bonus: save a screenshot!
    driver.save_screenshot(f'./screenshots/pythonscraping_{currentTime}.png')
    driver.quit()
    return final_df

def page_scrape():
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
    a_duration = []
    a_section_cities = []
    for n in section_a_list:
        # Separate the time from the cities
        a_section_cities.append(''.join(n.split()[2:5]))
        a_duration.append(''.join(n.split()[0:2]))
    b_duration = []
    b_section_cities = []
    for n in section_b_list:
        # Separate the time from the cities
        b_section_cities.append(''.join(n.split()[2:5]))
        b_duration.append(''.join(n.split()[0:2]))

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
        raise e
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
                                         'Out Duration': a_duration,
                                         'Out Cities': a_section_cities,
                                         'Return Day': b_day,
                                         'Return Weekday': b_weekday,
                                         'Return Duration': b_duration,
                                         'Return Cities': b_section_cities,
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

    city_from = Secrets.cities['orlando']
    city_to = Secrets.cities['san_francisco']
    date_start = '2022-07-10'
    date_end = '2022-07-13'

    return start_kayak(city_from, city_to, date_start, date_end)

#region old code
    # for n in range(0,5):
    #     start_kayak(city_from, city_to, date_start, date_end)
    #     print('iteration {} was complete @ {}'.format(n, strftime("%Y%m%d-%H%M")))

    #     # Wait 4 hours
    #     sleep(60*60*4)
    #     print('sleep finished.....')

#endregion




if __name__ == '__main__':
    df = main()
    print('Kayak plane ticket price scraping complete!')
