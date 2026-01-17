from enum import Enum
import os, sys
import ssl, certifi
import urllib.request
import datetime

class Student():
    def __init__(self, name, lesson_price=35, advance_payment=0, lesson_in_this_week=None, lessons=None):
        self.name = name
        self.lesson_price = lesson_price
        self.advance_payment = advance_payment
        self.lessons_in_this_week = lesson_in_this_week
        self.lessons = lessons

class LessonStatus(Enum):
    DEMO = 0 # Pale blue
    PENDING = 1 # Purple / Lavender
    PAID = 2 # Pale green / Sage
    UNPAID = 11 # Red / Tomato

def get_base_path():
    """Return the folder where the exe/script lives."""
    if getattr(sys, "frozen", False):  # Running as bundled exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))  # Running as .py script

def weekday_to_text(time_input: datetime.datetime):
    index = time_input.weekday()
    if index == 0:
        return "Monday"
    elif index == 1:
        return "Tuesday"
    elif index == 2:
        return "Wednesday"
    elif index == 3:
        return "Thursday"
    elif index == 4:
        return "Friday"
    elif index == 5:
        return "Saturday"
    elif index == 6:
        return "Sunday"
    else:
        raise Exception("Invalid weekday index.")


class ConnectionChecker():

    """
    Check internet connection by trying to reach https://www.google.com.
    Returns True if connected, False otherwise.
    """
    @staticmethod
    def is_internet_connection_present() -> bool:
        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            urllib.request.urlopen("https://www.google.com", timeout=5, context=ssl_context)
            return True
        except Exception:
            return False
        
def set_terminal_size(rows=40, cols=120):
    """
    Set the terminal window size on macOS.
    
    rows: number of text rows
    cols: number of text columns
    """
    # The escape sequence for resizing terminal
    # \e[8;<rows>;<cols>t
    sys.stdout.write(f"\033[8;{rows};{cols}t")
    sys.stdout.flush()