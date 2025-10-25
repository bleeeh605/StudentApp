from enum import Enum
import os, sys
import ssl, certifi
import urllib.request

class Student():
    def __init__(self, name, lesson_price=35, advance_payment=0, lesson_in_this_week=None, lessons=None):
        self.name = name
        self.lesson_price = lesson_price
        self.advance_payment = advance_payment
        self.lessons_in_this_week = lesson_in_this_week
        self.lessons = lessons

class LessonStatus(Enum):
    PENDING = 1 # Purple / Lavender
    PAID = 2 # Pale green / Sage
    UNPAID = 11 # Red / Tomato

def get_base_path():
    """Return the folder where the exe/script lives."""
    if getattr(sys, "frozen", False):  # Running as bundled exe
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))  # Running as .py script

def weekday_to_text(weekday_index):
    if weekday_index == 0:
        return "Monday"
    elif weekday_index == 1:
        return "Tuesday"
    elif weekday_index == 2:
        return "Wednesday"
    elif weekday_index == 3:
        return "Thursday"
    elif weekday_index == 4:
        return "Friday"
    elif weekday_index == 5:
        return "Saturday"
    elif weekday_index == 6:
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