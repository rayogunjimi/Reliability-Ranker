from selenium import webdriver
from selenium.webdriver.common.by import By

import os
import time
import random as rnd

driver = webdriver.Chrome('chromedriver')
#driver = webdriver.Firefox()
model_counter = 0
vehicle_ids = []

# enter or return
area_code = "19085\ue007" #\ue006

url = "https://www.carfax.com"
#path = os.getcwd()
path = os.path.dirname(__file__)

def waiter(lower_lim = 0.05, upper_lim = 0.1):
    driver.implicitly_wait(rnd.uniform(lower_lim, upper_lim))
    time.sleep(rnd.uniform(lower_lim, upper_lim))

def set_viewport_size(driver, width=1920, height=1080):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)

def set_filters():
    waiter()
    driver.find_element(by=By.XPATH, value='//span[@aria-label="Toggle noAccidents"]').click()
    waiter()
    driver.find_element(by=By.XPATH, value='//span[@aria-label="Toggle oneOwner"]').click()
    waiter()
    driver.find_element(by=By.XPATH, value='//span[@aria-label="Toggle personalUse"]').click()
    waiter()
    driver.find_element(by=By.XPATH, value='//span[@aria-label="Toggle serviceRecords"]').click()

def parse_listings():
    waiter()

    listings = driver.find_elements(by=By.XPATH, value='//article[@class="srp-list-item show-cta"]')
    vins_file = open(path + "/vins.csv","a")
    for listing_index in range(len(listings)):
        vehicle_ids.append(listings[listing_index].get_attribute("data-vin"))
        vins_file.write(listings[listing_index].get_attribute("data-vin") + "\n")
    vins_file.close()

    try:
        # For single page there is no button at all.
        if(driver.find_element(by=By.XPATH, value='//button[@class="button primary-blue pagination__button pagination__button--right "]').is_enabled()):
            driver.find_element(by=By.XPATH, value='//button[@class="button primary-blue pagination__button pagination__button--right "]').click()
            parse_listings()
        # Return is necessary to get back to homepage. Why?
        return
    except:
        print("Couldn't click button.")

def iterate_models(model_counter = 0):
    waiter()

    models = driver.find_elements(by=By.XPATH, value='//option[@class="model-option"]')

    if((len(models)) > model_counter):
        print("Current model:", models[model_counter].text)
        models[model_counter].click()
    else:
        print("Model requested: ", model_counter, ". Models found: ", len(models), ". Returning.")
        return

    #driver.find_element(by=By.XPATH, value='//option[@id="make_All"]').click
    #driver.find_element(by=By.XPATH, value='//option[@id="model_All"]').click()

    waiter()
    driver.find_element(by=By.XPATH, value='//input[@class=" search-zip ui-input search-zip--lp null"]').send_keys(area_code)

    try:
        set_filters()
    except:
        print("Filters could not be found.")
        waiter()
        driver.find_element(by=By.XPATH, value='//button[text()="Next"]').click()
        set_filters()

    try:
        waiter()
        driver.find_element(by=By.XPATH, value='//div[@class="showMeResults--lp showMeResults-float--lp"]').click()

        try:
            waiter()
            driver.find_element(by=By.XPATH, value='//option[@id="mileageDesc"]').click()
        except:
            print("Could not sort listings by mileage.")

        try:
            parse_listings()
        except:
            print("Unable to to parse the listings.")

        driver.back()

        if((model_counter) < (len(models) - 1)):
            iterate_models(model_counter + 1)

    except:
        waiter()
        driver.back()
        if((model_counter) < (len(models) - 1)):
            iterate_models(model_counter + 1)

def iterate_makes(make_counter = 0, make_limit = 0, limiter = 1):
    waiter()

    makes = driver.find_elements(by=By.XPATH, value='//option[@class="make-option"]')

    if((len(makes)) > make_counter):
        print("len(makes):", len(makes))
        print("Current make:", makes[make_counter].text)
        makes[make_counter].click()
    else:
        print("Make requested: ", make_counter , ". Makes found: ", len(makes), ". Retruning.")
        return

    iterate_models()

    if( (make_counter) < int(limiter*make_limit) + int((not limiter)*(len(makes) - 1)) ):
        iterate_makes(make_counter + 1)


def main():
    #chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    #chrome_options.add_argument('--no-sandbox')
    #chrome_options.add_argument('--disable-dev-shm-usage')
    #driver = webdriver.Chrome('chromedriver', options=chrome_options)

    set_viewport_size(driver, 1280, 720)

    global url
    driver.get(url + '/cars-for-sale')

    #print(driver.current_url())
    #driver.save_screenshot('screenshot.png')
    
    print("Please spolve CAPTCHA.")
    waiter(20, 30)

    print("Collecting VINs.")
    iterate_makes()
    print("VINs collected.")

    driver.quit()

if __name__ == "__main__":
    main()
