import curses

from menu import Menu, create_lazy_menu_callback
from calendar_manager import CalendarEvent
from utility import ConnectionChecker, LessonStatus

class MenuCreateLesson(Menu):
    
    def __init__(self, stdscr, calendar):
        self._calendar = calendar
        self._event = CalendarEvent("(Untitled)")
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item(f"Name: {self._event.name}", self._create_enter_event_parameter_callback("name")),
                      Menu.Item(f"Date: {self._event.date}", self._create_enter_event_parameter_callback("date")),
                      Menu.Item(f"Start hour: {self._event.start_hour}", self._create_enter_event_parameter_callback("start hour")),
                      Menu.Item(f"Duration: {self._event.duration}", self._create_enter_event_parameter_callback("duration")),
                      Menu.Item(f"Status: {self._event.status}", create_lazy_menu_callback(SelectStatus, self._stdscr, self._event.status, self._refresh_items)),
                      Menu.Item("Create", self._confirm_event_callback)]
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _create_enter_event_parameter_callback(self, option):
        def create_enter_event_parameter():
            curses.curs_set(1)     # show cursor
            self._stdscr.clear()
            input_str = ""

            while True:
                self._stdscr.clear()
                self._stdscr.addstr(0, 0, f"Type the {option} of the lesson and press Enter. Press ESC to go back.")
                format_string = ""
                if option == "name":
                    format_string = "Format: [Text]."
                elif option == "date":
                    format_string = "Format: [YYYY-MM-DD]."
                elif option == "start_hour":
                    format_string = "Format: [HH:mm]."
                elif option == "duration":
                    format_string = "Format: [Number] as minutes."
                elif option == "status":
                    format_string = "Format: [1 (Pending), 2 (Paid), or 11 (Unpaid)]."
                self._stdscr.addstr(2, 0, f"{format_string} Current input: " + input_str)

                key = self._stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_str.strip():
                        # TODO: Accept spaces for surnames?
                        if option == "name":
                            self._event.name = input_str.strip()
                        elif option == "date":
                            self._event.date = input_str.strip()
                        elif option == "start hour":
                            self._event.start_hour = input_str.strip()
                        elif option == "duration":
                            if input_str.strip().isdigit():
                                input = float(input_str.strip())
                                if 0 < input <= 120: # currently limited between 1 minute and 2 hours
                                    self._event.duration = input
                        elif option == "status":
                            self._event.status = input_str.strip()
                        self._refresh_items()
                        break # back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_str = input_str[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_str += chr(key)
        return create_enter_event_parameter
    
    def _confirm_event_callback(self):
        if ConnectionChecker.is_internet_connection_present():
            self._calendar.create_event(self._event)
        else:
            self._stdscr.clear()
            h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
            error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
            x = w//2 - round(len(error_string)//2)        # Calculate x so text is centered horizontally
            y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
            # TODO: Find out why this causes a crash in the .exe variant with x,y
            self._stdscr.addstr(0, 0, error_string)
            self._stdscr.refresh()
            self._stdscr.getch()  # Wait for key press before going back
        return "BACK"  # Return to previous menu

class SelectStatus(Menu):

    def __init__(self, stdscr, status, refresh_callback):
        self._status = status
        self._refresh_callback = refresh_callback
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        for status in LessonStatus:
            self._items.append(Menu.Item(LessonStatus(status).name, self._select_status_callback(status.value)))
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _select_status_callback(self, status):
        self._status = status
        self._refresh_callback()
