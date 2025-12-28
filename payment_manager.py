from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from utility import LessonStatus, Student, ConnectionChecker, weekday_to_text

class PaymentManager():

    def __init__(self, stdscr, data_base, calendar):
        self._stdscr = stdscr
        self._data_base = data_base
        self._calendar = calendar
    
    def do_routine(self) -> None:
        self._stdscr.clear()  # Clear the screen before redrawing

        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
        x = w//4
        y = h//4
        self._stdscr.addstr(y, x, "Connecting...")
        self._stdscr.refresh()

        if not ConnectionChecker.is_internet_connection_present():
            self._display_connection_unaveilable(x, y)
            return
        
        self._stdscr.addstr(y, x, "Doing an automated update for students. Please wait...")
        self._stdscr.refresh()

        updated_students = self._automatic_student_update()

        self._stdscr.clear()  # Clear the screen before redrawing
        update_text_strings = self._create_updated_students_texts(updated_students)
        self._show_update_text(update_text_strings, x, y)

    def _display_connection_unaveilable(self, x: int, y: int) -> None:
            self._stdscr.clear()  # Clear the screen before redrawing
            self._stdscr.addstr(y + 1, x, "Connection could not be established. Check your internet connection if you want to use ")
            self._stdscr.addstr(y + 2, x, "full program functionality. Press any key to continue...")
            self._stdscr.refresh()
            self._stdscr.getch()

    def _automatic_student_update(self) -> list[tuple]:
        updated_students = []
        # Get information for all students
        student_rows = self._data_base.get_students_info()
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        month_earlier = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_earlier = month_earlier + timedelta(days=-30)
        # For each student: Search for lessons with this student in the past month
        for student_row in student_rows:
            student_id, name, lesson_price, advance_payment = student_row
            lessons = self._calendar.get_student_lessons_in_selected_period(name, month_earlier, now)
            # For each such lesson:
            for lesson in lessons:
                # If lesson is not yet paid
                color = lesson.get("colorId")
                if color != str(LessonStatus.PAID.value):
                    if color == str(LessonStatus.DEMO.value) or color is None:
                        continue
                    # If their advance payment is enough to cover their lesson price
                    if advance_payment >= lesson_price:
                        # Reduce payment in advance and patch event and update data base
                        advance_payment -= lesson_price
                        # Mark lesson as paid
                        self._calendar.edit_event(lesson, color_id=str(LessonStatus.PAID.value))
                        self._data_base.edit_student(student_id=student_id, student=Student(name=name, lesson_price=lesson_price, advance_payment=advance_payment))
                        updated_students.append((name, lesson, "paid"))
                    elif color != str(LessonStatus.UNPAID.value):
                        # Otherwise mark lesson as unpaid
                        self._calendar.edit_event(lesson, color_id=str(LessonStatus.UNPAID.value))
                        updated_students.append((name, lesson, "unpaid"))
        return updated_students

    def _create_updated_students_texts(self, updated_students: list[tuple]) -> list[str]:
        update_text_strings = []
        if updated_students:
            for update in updated_students:
                lesson_start_date = update[1]['start'].get('dateTime', update[1]['start'].get('date'))
                lesson_start_date = datetime.fromisoformat(lesson_start_date)
                update_string = f"{update[0]}'s lesson on {lesson_start_date.strftime('%d.%m.%Y')} ({weekday_to_text(lesson_start_date)}) was marked as {update[2]}."
                update_text_strings.append(update_string)
        return update_text_strings
    
    def _show_update_text(self, text_strings: list[str], x: int, y: int) -> None:
        if text_strings:
            for index, text in enumerate(text_strings):
                if index == 0:
                    text = "Update: " + text
                y += index
                self._stdscr.addstr(y, x, text)
            self._stdscr.addstr(y+1, x, "Press any key to continue...")
        else:
            self._stdscr.addstr(y, x, "No automated updates were needed.")
            self._stdscr.addstr(y+2, x, "Press any key to continue...")
        self._stdscr.refresh()
        self._stdscr.getch()
