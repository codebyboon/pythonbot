import pywhatkit
import pyautogui
from pynput.keyboard import Key, Controller

# access secret keys for the project
from dotenv import dotenv_values
import os

# params
secrets = dotenv_values('.env')
keyboard = Controller()


def send_message(bookingdate, bookingday):
    # def send_message():
    try:
        msg = "Hi everyone, successfully booked badminton court on ", bookingday, "(", bookingdate, "). Let us know if you cannot make it."

        pywhatkit.sendwhatmsg_to_group_instantly(
            group_id=secrets['WHATSAPP_1'],
            message=msg,
        )
        # time.sleep(10)
        pyautogui.click()
        # time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        print("Message sent!")
    except Exception as e:
        print(str(e))
