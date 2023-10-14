import sys

from typing import Tuple
from time import sleep
from datetime import time, datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from joblib import Parallel, delayed

from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# access secret keys for the project
from dotenv import dotenv_values

# params
secrets = dotenv_values('.env')
booking_site_url = secrets['URL']
court_url = secrets['COURT_URL'] + sys.argv[1] + '/IBC2'
begin_time = time(00, 00)
end_time = time(00, 15)

myt = timezone(timedelta(hours=+8), 'MYT')


def check_current_time(begin_time: time, end_time: time) -> Tuple[time, bool]:
    '''
    Check current time is between 00:00 and 00:15. 
    Returns current time and if it is between begin and end time.
    '''
    dt_now = datetime.now(myt)
    current_time = time(dt_now.hour, dt_now.minute, dt_now.second)
    return current_time, (begin_time <= current_time) and (current_time < end_time)


# def make_a_reservation(reservation_time:int, reservation_name:str) -> bool:
def make_a_reservation() -> bool:
    '''
    Make a reservation for the given time and name at the booking site.
    Return the status if the reservation is made successfully or not.
    '''
    try:
        # Open google chrome with the website
        options = Options()
        # comment out this line to see the process in chrome
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options)
        driver.get(booking_site_url)

        # Click Login button at homepage
        # Commented out since the element has been changed.
        # driver.find_element(By.ID, 'menu-item-2273').click()

        # Auto submit username & password then click Login button
        driver.find_element(By.NAME, 'username').send_keys(
            secrets['USERNAME'])

        driver.find_element(By.NAME, 'password').send_keys(secrets['PASSWORD'])

        driver.find_element(
            By.XPATH, '//*[@id="loginForm"]/div/div[3]/input[1]').click()
        
        # Navigate straight to the court and Get all badminton time slot and select latest available slot
        driver.get(court_url)

        # initialize the params
        current_time, running_time = check_current_time(begin_time, end_time)

        # repreat booking a reservation every second
        while True:
            if not running_time:
                print(
                    f'Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')

                if current_time >= time(23, 59, 59):
                    sleep(0.001)
                elif time(23, 59, 58) <= current_time < time(23, 59, 59):
                    sleep(0.05)
                else:
                    sleep(1)

                current_time, running_time = check_current_time(
                    begin_time, end_time)
                continue

            wait = WebDriverWait(driver, 20)  # Adjust the timeout as needed
            driver.refresh()

            # Add a wait for the element to be clickable after the refresh
            
            # element = wait.until(EC.element_to_be_clickable((By.NAME, 'bookingTime')))
            elements = wait.until(EC.presence_of_all_elements_located((By.NAME, 'bookingTime')))
            elements[-1].click()

            # Click add booking button after selecting latest time
            driver.find_element(
                By.XPATH, '//*[@id="main"]/div/div/form/table/tbody/tr[15]/td/input').click()

            try:
                # Click Reserve button
                driver.find_element(
                    By.XPATH, '//*[@id="add-booking"]/div/form[1]/div[6]/button').click()
            except NoSuchElementException:
                print('Cannot find Reserve button')

            booked_time = driver.find_element(
                By.NAME, 'displayStartTime').get_attribute('value')
            
            # Click Confirm button
            driver.find_element(
                By.XPATH, '//*[@id="add-booking"]/div[1]/div[11]/button[2]').click()
                
            
            return True, booked_time
    except Exception as e:
        # print(e)
        return False

def try_booking() -> None:
    '''
    Try booking a reservation until either one reservation is made successfully
    '''
    # initialize the params
    reservation_completed = False

    # try to get ticket
    # reservation_completed = make_a_reservation(reservation_time, reservation_name)
    reservation_completed, reserved_time = make_a_reservation()

    if reservation_completed:

        print('Reserved one session successfully at', reserved_time)
    else:
        print('Failed to book')



if __name__ == '__main__':
    try:
        try_booking()
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
