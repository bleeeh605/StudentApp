from enum import Enum

version = "1.0.0"

class Student():
    def __init__(self, name, lesson_price=35, advance_payment=0, lesson_in_this_week=None, lessons=None):
        self.name = name
        self.lesson_price = lesson_price
        self.advance_payment = advance_payment
        self.lessons_in_this_week = lesson_in_this_week
        self.lessons = lessons

class LessonStatus(Enum):
    PENDING = 0 # Pale blue / Peacock
    PAID = 2 # Pale green / Sage
    UNPAID = 11 # Red / Tomato