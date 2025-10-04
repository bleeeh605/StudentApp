from enum import Enum
import os, sys

version = "1.0.0"

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