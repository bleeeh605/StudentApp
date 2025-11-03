import curses

from menu import Menu, create_lazy_menu_callback
from calendar_manager import CalendarEvent
from utility import ConnectionChecker, LessonStatus

class MenuCreateLesson(Menu):
    
    def __init__(self, stdscr, data_base, calendar):
        self._data_base = data_base
        self._calendar = calendar
        self._event = CalendarEvent("---")
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item(f"Name: {self._event.name}", create_lazy_menu_callback(SelectValueMenu, self._stdscr, self._data_base, self._event, value_type="name", refresh_callback=self._refresh_items)),
                      Menu.Item(f"Date: {self._event.date}", self._create_enter_event_parameter_callback("date")),
                      Menu.Item(f"Start hour: {self._event.start_hour}", self._create_enter_event_parameter_callback("start hour")),
                      Menu.Item(f"Duration: {self._event.duration}", self._create_enter_event_parameter_callback("duration")),
                      Menu.Item(f"Status: {self._event.status.name}", create_lazy_menu_callback(SelectValueMenu, self._stdscr, self._data_base, self._event, value_type="status", refresh_callback=self._refresh_items)),
                      Menu.Item("Create", self._confirm_event_callback)]
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _create_enter_event_parameter_callback(self, option):
        def create_enter_event_parameter():
            curses.curs_set(1)     # show cursor
            self._stdscr.clear()
            input_string = ""

            while True:
                self._stdscr.clear()
                self._stdscr.addstr(0, 0, f"Type the {option} of the lesson and press Enter. Press ESC to go back.")
                format_string = ""
                if option == "date":
                    format_string = "Format: [YYYY-MM-DD]."
                    #input_str = self._event.date
                elif option == "start_hour":
                    format_string = "Format: [HH:mm]."
                    #input_str = self._event.start_hour
                elif option == "duration":
                    format_string = "Format: [Number] as minutes."
                    #input_str = self._event.duration
                else:
                    pass
                    #input_str = ""
                self._stdscr.addstr(2, 0, f"{format_string} Current input: " + input_string)

                key = self._stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_string.strip():
                        if option == "name":
                            self._event.name = input_string.strip()
                        elif option == "date":
                            self._event.date = input_string.strip()
                        elif option == "start hour":
                            self._event.start_hour = input_string.strip()
                        elif option == "duration":
                            if input_string.strip().isdigit():
                                input_float = float(input_string.strip())
                                if 0 < input_float <= 120: # currently limited between 1 minute and 2 hours
                                    self._event.duration = input_float
                        self._refresh_items()
                        break # back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_string = input_string[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_string += chr(key)
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

class SelectValueMenu(Menu):

    def __init__(self, stdscr, data_base, lesson, value_type, refresh_callback):
        self._data_base = data_base
        self._lesson = lesson
        self._value_type = value_type
        self._refresh_callback = refresh_callback
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        if self._value_type == "status":
            for status in LessonStatus:
                self._items.append(Menu.Item(status.name, self._create_select_value_callback(status)))
        elif self._value_type == "name":
            students_info = self._data_base.get_students_info()
            for info in students_info:
                name = info[1]
                self._items.append(Menu.Item(name, self._create_select_value_callback(name)))
        else:
            raise Exception("Invalid value type provided.")
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _create_select_value_callback(self, value):
        def _select_value_callback():
            if self._value_type == "status":
                self._lesson.status = value
            elif self._value_type == "name":
                self._lesson.name = value
            else:
                raise Exception("Invalid value type provided.")
            self._refresh_callback()
            return "BACK"
        return _select_value_callback
