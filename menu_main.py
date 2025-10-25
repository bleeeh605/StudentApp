from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from menu import Menu, create_lazy_menu_callback
from utility import Student, ConnectionChecker, LessonStatus, weekday_to_text
from menu_students_overview import MenuStudentsOverview
from menu_add_or_edit_student import MenuAddOrEditStudent
from menu_remove_student import MenuRemoveStudent
from menu_create_lesson import MenuCreateLesson

BUDGET_CALCULATION_START_DATE = datetime(
    2025, 9, 1, 0, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))


class MenuMain(Menu):

    def __init__(self, stdscr, data_base, calendar, update_lessons=None):
        super().__init__(stdscr)
        self._data_base = data_base
        self._calendar = calendar
        self._update_lessons = update_lessons

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item("Update lessons", self._update_lessons_callback),
                       Menu.Item("Budget", self._calculate_budget_callback),
                       Menu.Item("Add students", create_lazy_menu_callback(MenuAddOrEditStudent, self._stdscr, self._data_base, action="add", student=Student("---"))),
                       Menu.Item("Remove students", create_lazy_menu_callback(
                           MenuRemoveStudent, self._stdscr, self._data_base)),
                       Menu.Item("Edit students", create_lazy_menu_callback(
                           MenuStudentsOverview, self._stdscr, self._data_base)),
                       Menu.Item("Create lesson", create_lazy_menu_callback(
                           MenuCreateLesson, self._stdscr, self._calendar)),
                       Menu.Item("Show upcoming events",
                                 self._list_events_callback),
                       
                       Menu.Item("Exit", None)]

    def _list_events_callback(self):
        # TODO: Automatically determine the timezone of the computer
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        end_of_two_weeks_from_now = now.replace(
            hour=0, minute=0, second=0, microsecond=0)
        end_of_two_weeks_from_now = end_of_two_weeks_from_now + \
            timedelta(days=14, seconds=-1)

        self._stdscr.clear()
        if not ConnectionChecker.is_internet_connection_present():
            self._display_connection_unaveilable()
            return
        events = self._calendar.get_events_in_selected_period(
            now, end_of_two_weeks_from_now)
        self._display_events(events, now, end_of_two_weeks_from_now)

    def _display_events(self, events, start_time, end_time):
        # Get the height (h) and width (w) of the terminal window
        h, w = self._stdscr.getmaxyx()
        if not events:
            event_string = f"No events found in the selected period {start_time.strftime('%d.%m.%Y')} -> {end_time.strftime('%d.%m.%Y')}"
            # Calculate x so text is centered horizontally
            x = w//2 - round(len(event_string)//2)
            # Calculate y so the whole menu is vertically centered
            y = h//2 - 1
            # TODO: Find out why this causes a crash in the .exe variant
            self._stdscr.addstr(0, 0, event_string)
        else:
            for index, event in enumerate(events):
                event_begin = event["start"].get(
                    "dateTime", event["start"].get("date"))
                event_begin = datetime.fromisoformat(
                    event_begin)
                event_name = event["summary"]
                event_string = f"{event_name} -> {event_begin.strftime('%d.%m.%Y %H:%M')} ({weekday_to_text(event_begin)})"
                # Calculate x so text is centered horizontally
                x = w//2 - len(event_string)//2
                # Calculate y so the whole menu is vertically centered
                y = h//2 - len(events)//2 + index
                self._stdscr.addstr(y, x, event_string)
        self._stdscr.refresh()
        self._stdscr.getch()  # Wait for key press before going back
        # return "BACK"   # Return to previous menu

    def _display_connection_unaveilable(self):
        # Get the height (h) and width (w) of the terminal window
        h, w = self._stdscr.getmaxyx()
        error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
        # Calculate x so text is centered horizontally
        x = w//2 - round(len(error_string)//2)
        # Calculate y so the whole menu is vertically centered
        y = h//2 - 1
        # TODO: Find out why this causes a crash in the .exe variant
        self._stdscr.addstr(0, 0, error_string)
        self._stdscr.refresh()
        self._stdscr.getch()  # Wait for key press before going back

    def _calculate_budget_callback(self):
        budget = 0
        budget_this_month = 0

        if not ConnectionChecker.is_internet_connection_present():
            self._display_connection_unaveilable()
            return

        # Get the height (h) and width (w) of the terminal window
        h, w = self._stdscr.getmaxyx()
        x = w//3
        y = h//4
        self._stdscr.clear()  # Clear the screen before redrawing
        self._stdscr.addstr(y, x, "Calculating budget, please wait.")
        self._stdscr.refresh()
        # Get information for all students
        student_rows = self._data_base.get_students_info()
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        # For each student: Search for lessons with this student in the past month
        for student_row in student_rows:
            id, name, lesson_price, advance_payment = student_row
            lessons = self._calendar.get_student_lessons_in_selected_period(
                name, BUDGET_CALCULATION_START_DATE, now)
            # For each such lesson:
            for lesson in lessons:
                # If lesson is marked as paid
                if lesson.get("colorId") == str(LessonStatus.PAID.value):
                    budget += lesson_price
                    # Separate in function
                    event_date = lesson["start"].get(
                    "dateTime", lesson["start"].get("date"))
                    event_date = datetime.fromisoformat(event_date)
                    if event_date.year == now.year and event_date.month == now.month:
                        budget_this_month += lesson_price

        months_since_start_date = (now.year - BUDGET_CALCULATION_START_DATE.year) * \
            12 + now.month - BUDGET_CALCULATION_START_DATE.month
        budget_average_per_month = budget / \
            (months_since_start_date + 1)  # +1 for current month
        self._stdscr.clear()  # Clear the screen before redrawing
        self._stdscr.addstr(
            y, x, f"Total budget since {BUDGET_CALCULATION_START_DATE.strftime('%d.%m.%Y')}: {budget}€")
        self._stdscr.addstr(
            y+1, x, f"Average budget per month: {budget_average_per_month}€")
        self._stdscr.addstr(y+2, x, f"Total budget this month: {budget_this_month}€")
        self._stdscr.addstr(y+3, x, "Press any key to continue...")
        self._stdscr.refresh()
        self._stdscr.getch()

    def _update_lessons_callback(self):
        if self._update_lessons:
            self._update_lessons()
