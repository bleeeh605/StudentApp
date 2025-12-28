from datetime import datetime
from zoneinfo import ZoneInfo
import curses

from menu import Menu
from utility import ConnectionChecker, LessonStatus

class BudgetMenu(Menu):

    def __init__(self, stdscr, data_base, calendar):
        super().__init__(stdscr)
        self._data_base = data_base
        self._calendar = calendar
        start_date_isoformat = data_base.get_budget_start_date()[0]
        start_date = datetime.fromisoformat(start_date_isoformat)
        self._start_date = start_date.replace(tzinfo=ZoneInfo("UTC"))
        end_date_isoformat = data_base.get_budget_end_date()[0]
        end_date = datetime.fromisoformat(end_date_isoformat)
        self._end_date = end_date.replace(tzinfo=ZoneInfo("UTC"))

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item("Calculate budget", self._calculate_budget_callback),
                       Menu.Item(f"Start date: {self._start_date.strftime('%d.%m.%Y')}", self._create_enter_date_callback("start_date")),
                       Menu.Item(f"End date: {self._end_date.strftime('%d.%m.%Y')}", self._create_enter_date_callback("end_date")),
                       Menu.Item("Back", self._back_callback())]
        
    def _create_enter_date_callback(self, option):
        def enter_date_callback():
            curses.curs_set(1)     # show cursor
            self._stdscr.clear()
            input_string = ""

            while True:
                self._stdscr.clear()
                format_string = ""
                if option == "start_date":
                    self._stdscr.addstr(0, 0, f"Type the date since which you want the budget to be calculated from and press Enter. Press ESC to go back.")
                    format_string = "Format: [YYYY-MM-DD]."
                elif option == "end_date":
                    self._stdscr.addstr(0, 0, f"Type the date until which you want the budget to be calculated from and press Enter. Press ESC to go back.")
                    format_string = "Format: [YYYY-MM-DD]."
                else:
                    pass
                self._stdscr.addstr(2, 0, f"{format_string} Current input: " + input_string)

                key = self._stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                        self._handle_input(option, input_string)
                        self._refresh_items()
                        break # back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_string = input_string[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_string += chr(key)
        return enter_date_callback
    
    def _handle_input(self, option, input_string):
        if input_string.strip():
            if option == "start_date":
                time_string_isoformat = input_string + "T00:00:00"
                date = datetime.fromisoformat(time_string_isoformat)
                self._start_date = date.replace(tzinfo=ZoneInfo("Europe/Berlin"))
                self._data_base.set_budget_start_date(self._start_date.isoformat())
            elif option == "end_date":
                time_string_isoformat = input_string + "T00:00:00"
                date = datetime.fromisoformat(time_string_isoformat)
                self._end_date = date.replace(tzinfo=ZoneInfo("Europe/Berlin"))
                self._data_base.set_budget_end_date(self._end_date.isoformat())
        
    def _calculate_budget_callback(self):
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

        budget = self._calculate_budget()
        # months_since_start_date = (self._end_date.year - self._start_date.year) * 12 + self._end_date.month - self._start_date.month
        # budget_average_per_month = budget / (months_since_start_date + 1)  # +1 for current month
        self._stdscr.clear()  # Clear the screen before redrawing
        self._stdscr.addstr(y, x, f"Total budget from {self._start_date.strftime('%d.%m.%Y')} to {self._end_date.strftime('%d.%m.%Y')}: {budget}€")
        # self._stdscr.addstr(y+1, x, f"Average budget per month: {'{:.2f}'.format(budget_average_per_month)}€")
        # self._stdscr.addstr(y+2, x, f"Total budget this month: {budget_this_month}€")
        self._stdscr.addstr(y+3, x, "Press any key to continue...")
        self._stdscr.refresh()
        self._stdscr.getch()

    def _calculate_budget(self):
        budget = 0
        #budget_this_month = 0
        # Get information for all students
        student_rows = self._data_base.get_students_info()
        # For each student: Search for lessons with this student in the past month
        for student_row in student_rows:
            _, name, lesson_price, _ = student_row
            lessons = self._calendar.get_student_lessons_in_selected_period(name, self._start_date, self._end_date)
            # For each such lesson:
            for lesson in lessons:
                # If lesson is marked as paid
                if lesson.get("colorId") == str(LessonStatus.PAID.value):
                    budget += lesson_price
                    # If lesson is in the current month, add its cost to the budget for the month
                    event_date = lesson["start"].get("dateTime", lesson["start"].get("date"))
                    event_date = datetime.fromisoformat(event_date)
                    # if event_date.year == self._end_date.year and event_date.month == self._end_date.month:
                    #     budget_this_month += lesson_price
        return budget #, budget_this_month]

    def _display_connection_unaveilable(self):
        h, w = self._stdscr.getmaxyx() # Get the height (h) and width (w) of the terminal window
        error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
        x = w//2 - round(len(error_string)//2) # Calculate x so text is centered horizontally
        y = h//2 - 1 # Calculate y so the whole menu is vertically centered
        # TODO: Find out why this causes a crash in the .exe variant
        self._stdscr.addstr(0, 0, error_string)
        self._stdscr.refresh()
        self._stdscr.getch()  # Wait for key press before going back