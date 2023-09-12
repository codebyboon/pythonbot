from typing import Tuple
from time import sleep
from datetime import time, datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from joblib import Parallel, delayed

#import whatsapp msg python script
import whatsappmsg

# params
booking_site_url = 'https://www.ecommunity.my/'
begin_time = time(00,00)
end_time = time(0,15)
max_try = 500
# reservation_time and reservation_name are given as arguments when python script runs
#reservation_time = int(sys.argv[1])
#reservation_name = sys.argv[2]

options = Options()
# comment out this line to see the process in chrome
options.add_argument('--headless')
driver = webdriver.Chrome()
#driver = webdriver.Chrome(options=options)
    #'/Users/my_name/dev/stranger_bot/driver/chromedriver', 
    #options=options

myt = timezone(timedelta(hours=+8), 'MYT')


def check_current_time(begin_time:time, end_time:time) -> Tuple[time, bool]:
    '''
    Check current time is between 00:00 and 00:15. 
    Returns current time and if it is between begin and end time.
    '''
    dt_now = datetime.now(myt)
    current_time = time(dt_now.hour, dt_now.minute, dt_now.second)
    return current_time, (begin_time <= current_time) and (current_time < end_time)


#def make_a_reservation(reservation_time:int, reservation_name:str) -> bool:
def make_a_reservation() -> bool:
    '''
    Make a reservation for the given time and name at the booking site.
    Return the status if the reservation is made successfully or not.
    '''
    try:
        # Open google chrome with the website
        driver.get(booking_site_url)

        # Click Login button at homepage
        driver.find_element(By.ID, 'menu-item-2273').click()

        # Auto submit username & password then click Login button
        driver.find_element(By.NAME, 'username').send_keys('ah_boon95@hotmail.com')

        driver.find_element(By.NAME, 'password').send_keys('Jun2504!')

        driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/input[1]').click()

        # Click eBooking button/image
        driver.find_element(By.XPATH, '//*[@id="feature-icons"]/div/table/tbody/tr[1]/td[3]/a/div').click()

        # Click Badminton court
        driver.implicitly_wait(1)
        driver.find_element(By.XPATH, '/html/body/div[2]/section[1]/div/section[2]/div/a[3]/div').click()
            
        # initialize the params
        current_time, running_time = check_current_time(begin_time, end_time)
        try_num = 1


        # repreat booking a reservation every second
        while True:
            if not running_time:
                print(f'Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')

                if current_time >= time(23,59,59):
                   sleep(0.001)
                elif time(23,59,58) <= current_time < time(23,59,59):
                   sleep(0.05)
                else:
                   sleep(1)

                try_num += 1
                current_time, running_time = check_current_time(begin_time, end_time)
                continue

            print(f'----- try : {try_num} -----')
            # Agree to the T&C when it's 12.00a.m.
            driver.find_element(By.XPATH, '//*[@id="myModal"]/div/div/div[3]/button[1]').click()

            # Find Badminton available timeslot
            greybox = driver.find_elements(By.CLASS_NAME, 'date_cell')
            
            #If available dates are in next month, click arrow button first. Otherwise, select the latest date
            if greybox:
                greybox[-1].click()
            else:
                print("Cannot find available date")
                while not greybox:
                    driver.find_element(By.CLASS_NAME, 'arrow-right').click()
                    founddate = driver.find_elements(By.CLASS_NAME, 'date_cell')     
                    if founddate:
                        founddate[-1].click()
                        break
            
            latest = driver.find_elements(By.NAME, 'bookingTime')
            latest[-1].click()

            # Click add booking button after selecting latest time
            driver.find_element(By.XPATH, '//*[@id="main"]/div/div/form/table/tbody/tr[15]/td/input').click()
            
            #Click Reserve button
            driver.find_element(By.XPATH, '//*[@id="add-booking"]/div/form[1]/div[6]/button').click()

            #Click Confirm button
            driver.find_element(By.XPATH, '//*[@id="add-booking"]/div[1]/div[11]/button[2]').click()
            return True
    except Exception as e:
        print(e)
        return False
    finally:
	# close the drivers
        print("success")
        #driver.quit()


#def try_booking(reservation_time:int, reservation_name:str, max_try:int=1000) -> None:
def try_booking(max_try:int=1000) -> None:
    '''
    Try booking a reservation until either one reservation is made successfully or the attempt time reaches the max_try
    '''
    # initialize the params
    reservation_completed = False

    # try to get ticket
    #reservation_completed = make_a_reservation(reservation_time, reservation_name)
    reservation_completed = make_a_reservation()

    # Use Parallel to run multiple reservation attempts in parallel
    '''
    n_jobs = 4  # Set the number of parallel instances you want to run
    results = Parallel(n_jobs=n_jobs)(
        delayed(make_a_reservation)() for _ in range(n_jobs)
    '''

    if reservation_completed:

        print('Reserved a badminton court')

        #To auto send successful reservation msg to whatsapp group
        bookeddate = datetime.now() + timedelta(days=7)
        formattedDate = bookeddate.strftime('%Y-%m-%d')
        bookedday = bookeddate.strftime('%A')
        whatsappmsg.message(formattedDate, bookedday)
    else:
        print('Failed to book')

if __name__ == '__main__':    
    #try_booking(reservation_time, reservation_name, max_try)
    try_booking(max_try)