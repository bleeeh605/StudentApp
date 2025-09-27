from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from definitions import LessonStatus

class AdvancePaymentManager():

    def __init__(self, data_base, calendar):
        self.data_base = data_base
        self.calendar = calendar
    
    def do_routine(self):
        print("Doing an automated update for students who have advance payment... Please wait...")
        # Check for students with payments in advance
        student_rows = self.data_base.get_students_with_advance_payment()
        # -> For each student:
        # Search for lessons with this student in the past month
        for student_row in student_rows:
            id, name, lesson_price, advance_payment = student_row
            now = datetime.now(ZoneInfo("Europe/Berlin"))
            month_earlier = now.replace(hour=0, minute=0, second=0, microsecond=0) 
            month_earlier = month_earlier + timedelta(days=-30)
            lessons = self.calendar.get_student_lessons_in_selected_period(name, month_earlier, now)
            # -> For each such lesson:
            for lesson in lessons:
                # If lesson is unpaid
                #TODO: FIX!!
                if lesson.get("colorId") != str(LessonStatus.PAID.value):
                     # -> If their advance payment is enough to cover their lesson price
                    if advance_payment >= lesson_price:
                        # reduce payment in advance and patch event and update data base
                        advance_payment -= lesson_price
                        # Mark lesson as paid
                        self.calendar.edit_event(lesson, color_id=str(LessonStatus.PAID.value))
                        self.data_base.edit_student(student_id=id, payment_in_advance=advance_payment)

# Optionally check for lessons which are in the past but have their status as still not paid, mark them as yellow etc
            




