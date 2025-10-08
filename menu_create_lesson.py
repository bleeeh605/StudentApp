import curses

from menu import Menu, MenuItem
from calendar_manager import CalendarEvent, ConnectionChecker

class MenuCreateLesson(Menu):
    
    def __init__(self, stdscr, calendar):
        self.stdscr = stdscr
        self.calendar = calendar
        self.items = []
        self.event = CalendarEvent("(Untitled)")
        self._needs_refresh = False
        super().__init__(self.items, stdscr)

    def refresh_items(self):
        self.items = [MenuItem(f"Name: {self.event.name}", self.create_enter_event_parameter_callback("name")),
                      MenuItem(f"Date: {self.event.date}", self.create_enter_event_parameter_callback("date")),
                      MenuItem(f"Start hour: {self.event.start_hour}", self.create_enter_event_parameter_callback("start hour")),
                      MenuItem(f"Duration: {self.event.duration}", self.create_enter_event_parameter_callback("duration")),
                      MenuItem(f"Status: {self.event.status}", self.create_enter_event_parameter_callback("status")),
                      MenuItem("Create", self.create_confirm_event_callback())]
        self.items.append(MenuItem("Back", self.back_callback()))

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
                        self.set_needs_refresh_true()
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

    def run_menu(self):
        """
        Runs a given menu and returns the index of the chosen item.
        """
        current_row = 0  # Start at the first row
        self.refresh_items()

        while True:
            if self._needs_refresh:
                self.refresh_items()
                self._needs_refresh = False  # reset after refreshing

            self.print_menu(current_row) # Draw menu

            key = self.stdscr.getch() # Wait for the next key press
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(self.items)-1:
                current_row += 1
            elif key in [curses.KEY_ENTER, 10, 13]: # Current row was selected!
                action = self.items[current_row].callback
                if action:
                    result = action() # Call callback
                    if result == "BACK":
                        break
                else:
                    break

            # Redraw menu with updated selection
            self.print_menu(current_row)

    def set_needs_refresh_true(self):
        self._needs_refresh = True
    