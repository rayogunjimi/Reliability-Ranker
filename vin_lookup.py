from selenium import webdriver
from selenium.webdriver.common.by import By

import os
import pickle
import time
import random as rnd
import requests

driver = webdriver.Chrome('chromedriver')
#driver = webdriver.Firefox()
model_counter = 0
vehicle_ids = []

# enter/return
area_code = "19085\ue007" #\ue006

#path = os.getcwd()
path = os.path.dirname(__file__)

def waiter(lower_lim = 0.005, upper_lim = 0.01):
    driver.implicitly_wait(rnd.uniform(lower_lim, upper_lim))
    time.sleep(rnd.uniform(lower_lim, upper_lim))

def set_viewport_size(driver, width=1920, height=1080):
    window_size = driver.execute_script("""
        return [window.outerWidth - window.innerWidth + arguments[0],
          window.outerHeight - window.innerHeight + arguments[1]];
        """, width, height)
    driver.set_window_size(*window_size)

def save_cookies(link_to_save_from):
    global path
    global driver
    print("Saving all cookies.")
    pickle.dump(driver.get_cookies() , open(path + "/cookies.pkl","wb"))
    print("cookies saved")

def load_cookies():
    global path
    global driver
    cookies = pickle.load(open(path + "/cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

def get_data(vin, write_buffer):
    global path
    waiter()
    driver.get("https://www.carfax.com" + "/vehicle/" + vin)
    waiter()
    price = ""
    price = driver.find_element(by=By.XPATH, value="//span[@class='vehicle-header__price']").text
    waiter()
    driver.get(driver.find_element(by=By.XPATH, value='//button[text()="View FREE CARFAX Report "]').get_attribute("title"))
    waiter()

    owners = "1"
    dealer_name = body_type = engine_info = fuel = driveline = year_make_model = owned_state = odo = year_purch = ""

    #dealer_name = driver.find_element(by=By.XPATH, value="//div[@id='dealer-name']").text
    #dealer_name = driver.find_element(by=By.XPATH, value="//div[@id='dealer-name']/a").text
    dealer_name = driver.find_element(by=By.XPATH, value="//label[text()[normalize-space()='This CARFAX Report Provided by:']]/following-sibling::div").text
    body_type = driver.find_element(by=By.XPATH, value='//*[@id="headerBodyType"]').text
    engine_info = driver.find_element(by=By.XPATH, value='//*[@id="headerEngineInfo"]').text
    fuel = driver.find_element(by=By.XPATH, value='//*[@id="headerFuel"]').text
    driveline = driver.find_element(by=By.XPATH, value='//*[@id="headerDriveline"]').text
    year_make_model = driver.find_element(by=By.XPATH, value='//*[@id="headerMakeModelYear"]').text

    try:
        owned_state = driver.find_element(by=By.XPATH, value="//div[text()[normalize-space()='Owned in the following states/provinces']]/parent::td/following-sibling::td/div").text
        odo = driver.find_element(by=By.XPATH, value="//div[text()[normalize-space()='Last reported odometer reading']]/parent::td/following-sibling::td/div").text
        year_purch = driver.find_element(by=By.XPATH, value="//div[text()[normalize-space()='Year purchased']]/parent::td/following-sibling::td/div").text
    except Exception as e:
        print(e)
        print("Missing information for a vehicle.")

    write_buffer += ((dealer_name or "").replace("," or ";","") + ",")
    write_buffer += ((body_type or "").replace("," or ";","") + ",")
    write_buffer += ((engine_info or "").replace("," or ";","") + ",")
    write_buffer += ((fuel or "").replace("," or ";","") + ",")
    write_buffer += ((driveline or "").replace("," or ";","") + ",")
    write_buffer += ((year_make_model or "").replace("," or ";","") + ",")
    write_buffer += ((owned_state or "").replace("," or ";","") + ",")
    write_buffer += ((odo or "").replace(",", "").replace("," or ";","") + ",")
    write_buffer += ((year_purch or "").replace("," or ";","") + ",")
    write_buffer += ((price or "").replace("," or ";", "") + ",")

    services = driver.find_elements(by=By.XPATH, value="//li[text()[normalize-space()='Vehicle serviced']]/child::ul/li")
    readabe_services = []
    for service in services:
        readabe_services.append(service.text)
        write_buffer += (service.text + "|")

    write_buffer += (", ")

    service_locations = driver.find_elements(by=By.XPATH, value="//li[text()[normalize-space()='Vehicle serviced']]/parent::ul/parent::div/preceding-sibling::div/preceding-sibling::div/span/ul/li[4]")
    readable_service_locations = []
    for service_location in service_locations:
        readable_service_locations.append(service_location.text)
        write_buffer += (service_location.text + "|")

    #car_file.write(", ")

    write_buffer += ("\n")

    return write_buffer

def get_vehicle_info(vin, write_buffer):
    make = model = model_year = series = trim = type = plant_country = body_class = doors = weight = ""

    try:
        response = requests.get("https://vpic.nhtsa.dot.gov/api/" + "vehicles/DecodeVin/" + vin + "*BA?format=json")
        if response.status_code == 200:
            car_details = response.json()

            make = car_details.get("Results")[6].get("Value")
            model = car_details.get("Results")[8].get("Value")
            model_year = car_details.get("Results")[9].get("Value")
            series = car_details.get("Results")[11].get("Value")
            trim = car_details.get("Results")[12].get("Value")
            type = car_details.get("Results")[13].get("Value")
            plant_country = car_details.get("Results")[14].get("Value")
            body_class = car_details.get("Results")[22].get("Value")
            doors = car_details.get("Results")[23].get("Value")
            weight = car_details.get("Results")[27].get("Value")
        else:
            print("No vehicle details. Returning.")
    except Exception as e:
        print(e)

    

    write_buffer += ((vin or "").replace("," or ";","") + ",")
    write_buffer += ((make or "").replace("," or ";","") + ",")
    write_buffer += ((model_year or "").replace("," or ";","") + ",")
    write_buffer += ((model or "").replace("," or ";","") + ",")
    write_buffer += ((series or "").replace("," or ";","") + ",")
    write_buffer += ((trim or "").replace("," or ";","") + ",")
    write_buffer += ((type or "").replace("," or ";","") + ",")
    write_buffer += ((plant_country or "").replace("," or ";","") + ",")
    write_buffer += ((body_class or "").replace("," or ";","") + ",")
    write_buffer += ((doors or "").replace("," or ";","") + ",")
    write_buffer += ((weight or "").replace("," or ";","").replace(" - ", "-") + ",")

    return write_buffer


def main():
    set_viewport_size(driver, 1280, 720)

    global path

    driver.get("https://www.carfax.com" + '/cars-for-sale')

    print(driver.current_url)
    driver.save_screenshot(path + '/screenshot.png')

    load_cookies()

    car_file = open(path + "/car_data.csv","w")
    car_file.write("vin,make,model,model_year,series,trim,type,plant_country,body_class,num_of_doors,curb_weight,"+
        "dealer_name,body_type,engine_info,fuel_type,driveline,year_make_model,owned_state,odo_reading,year_purchased,price,services,service_locations\n")
    car_file.close()

    print("Reading VINs file.")
    vins_file = open(path + "/vins_nodupes.csv","r")
    vins = vins_file.readlines()
    print("Collecting data on VINs.")

    for vehicle_id in vins:
        vehicle_id = (vehicle_id or "").replace("\n", "")
        nosuccess = True
        while(nosuccess):
            try:
                write_buffer = ""
                write_buffer = get_vehicle_info(vehicle_id, write_buffer)
                write_buffer = get_data(vehicle_id, write_buffer)
                nosuccess = False
                car_file = open(path + "/car_data.csv","a")
                car_file.write(write_buffer)
                car_file.close()
            except Exception as e:
                print(e)
                os.system('afplay /System/Library/Sounds/Sosumi.aiff')
                os.system(f"say {'There was an exception pulling a report. User input required.'}")
                command = input(f"Problem getting report. Clearing buffer. VIN: {vehicle_id} Press enter or type skip. Command: ")
                write_buffer = ""
                if command.lower().strip() == "skip":
                    break
                else:
                    continue
        nosuccess = True
    save_cookies()
    vins_file.close()
    vins.clear()
    print("Data on VINs collected.")

    driver.quit()

if __name__ == "__main__":
    main()