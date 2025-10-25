from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utility import LessonStatus, Student, ConnectionChecker

class PaymentManager():

    def __init__(self, stdscr, data_base, calendar):
        self._stdscr = stdscr
        self._data_base = data_base
        self._calendar = calendar
    
    def do_routine(self):
        self._stdscr.clear()  # Clear the screen before redrawing
        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
        x = w//4
        y = h//4
        self._stdscr.addstr(y, x, "Connecting...")
        if not ConnectionChecker.is_internet_connection_present():
            self._stdscr.addstr(y + 1, x, "Connection could not be established. Check your internet connection if you want to use ")
            self._stdscr.addstr(y + 2, x, "full program functionality. Press any key to continue...")
            self._stdscr.getch()
            return
        
        updated_students = []
        self._stdscr.clear()
        self._stdscr.addstr(y, x, "Doing an automated update for students. Please wait...")
        # Get information for all students
        student_rows = self._data_base.get_students_info()
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        month_earlier = now.replace(hour=0, minute=0, second=0, microsecond=0) 
        month_earlier = month_earlier + timedelta(days=-30)
        # For each student: Search for lessons with this student in the past month
        for student_row in student_rows:
            id, name, lesson_price, advance_payment = student_row
            lessons = self._calendar.get_student_lessons_in_selected_period(name, month_earlier, now)
            # For each such lesson:
            for lesson in lessons:
                # If lesson is not yet paid
                if lesson.get("colorId") != str(LessonStatus.PAID.value):
                    # If their advance payment is enough to cover their lesson price
                    if advance_payment >= lesson_price:
                        # Reduce payment in advance and patch event and update data base
                        advance_payment -= lesson_price
                        # Mark lesson as paid
                        self._calendar.edit_event(lesson, color_id=str(LessonStatus.PAID.value))
                        self._data_base.edit_student(student_id=id, student=Student(name=name, advance_payment=advance_payment))
                        updated_students.append((name, lesson, "paid"))
                    elif lesson.get("colorId") != str(LessonStatus.UNPAID.value):
                        # Otherwise mark lesson as unpaid
                        self._calendar.edit_event(lesson, color_id=str(LessonStatus.UNPAID.value))
                        updated_students.append((name, lesson, "unpaid"))
            # TODO: Optionally check for lessons which are in the past but have their status as still not paid, mark them as yellow etc
        if updated_students:
            self._stdscr.clear()  # Clear the screen before redrawing
            for index, update in enumerate(updated_students):
                lesson_start_date = update[1]['start'].get('dateTime', update[1]['start'].get('date'))
                update_string = f"{update[0]}'s lesson {lesson_start_date} was marked as {update[2]}."
                if index == 0:
                    update_string = "Update: " + update_string
                y += index
                self._stdscr.addstr(y, x, update_string)
            self._stdscr.addstr(y+1, x, "Press any key to continue...")
        else:
            self._stdscr.addstr(y+1, x, "No automated updates were needed. Press any key to continue...")
        self._stdscr.getch()
