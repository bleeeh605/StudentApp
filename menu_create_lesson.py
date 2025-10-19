import curses

from menu import Menu, create_lazy_menu_callback
from calendar_manager import CalendarEvent
from utility import ConnectionChecker, LessonStatus

class MenuCreateLesson(Menu):
    
    def __init__(self, stdscr, calendar):
        self.stdscr = stdscr
        self.calendar = calendar
        self.event = CalendarEvent("(Untitled)")
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        self.items = [Menu.Item(f"Name: {self.event.name}", self.create_enter_event_parameter_callback("name")),
                      Menu.Item(f"Date: {self.event.date}", self.create_enter_event_parameter_callback("date")),
                      Menu.Item(f"Start hour: {self.event.start_hour}", self.create_enter_event_parameter_callback("start hour")),
                      Menu.Item(f"Duration: {self.event.duration}", self.create_enter_event_parameter_callback("duration")),
                      Menu.Item(f"Status: {self.event.status}", create_lazy_menu_callback(SelectStatus, self.stdscr, self.event.status, self.refresh_items)),
                      Menu.Item("Create", self.create_confirm_event_callback())]
        self.items.append(Menu.Item("Back", self.back_callback()))

    def create_enter_event_parameter_callback(self, option):
        def create_enter_event_parameter():
            curses.curs_set(1)     # show cursor
            self.stdscr.clear()
            input_str = ""

            while True:
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, f"Type the {option} of the lesson and press Enter. Press ESC to go back.")
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
                self.stdscr.addstr(2, 0, f"{format_string} Current input: " + input_str)

                key = self.stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_str.strip():
                        # TODO: Accept spaces for surnames?
                        if option == "name":
                            self.event.name = input_str.strip()
                        elif option == "date":
                            self.event.date = input_str.strip()
                        elif option == "start hour":
                            self.event.start_hour = input_str.strip()
                        elif option == "duration":
                            if input_str.strip().isdigit():
                                input = float(input_str.strip())
                                if 0 < input <= 120: # currently limited between 1 minute and 2 hours
                                    self.event.duration = input
                        elif option == "status":
                            self.event.status = input_str.strip()
                        self.refresh_items()
                        break # back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_str = input_str[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_str += chr(key)
        return create_enter_event_parameter
    
    def create_confirm_event_callback(self):
        def create_confirm_event():
            if ConnectionChecker.is_internet_connection_present():
                self.calendar.create_event(self.event)
            else:
                self.stdscr.clear()
                h, w = self.stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
                error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
                x = w//2 - round(len(error_string)//2)        # Calculate x so text is centered horizontally
                y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
                # TODO: Find out why this causes a crash in the .exe variant with x,y
                self.stdscr.addstr(0, 0, error_string)
                self.stdscr.refresh()
                self.stdscr.getch()  # Wait for key press before going back
            return "BACK"  # Return to previous menu
        return create_confirm_event

class SelectStatus(Menu):

    def __init__(self, stdscr, status, refresh_callback):
        self.stdscr = stdscr
        self.status = status
        self.refresh_callback = refresh_callback
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        for status in LessonStatus:
            self.items.append(Menu.Item(LessonStatus(status).name, self.select_status_callback(status.value)))
        self.items.append(Menu.Item("Back", self.back_callback()))

    def select_status_callback(self, status):
        self.status = status
        self.refresh_callback()
