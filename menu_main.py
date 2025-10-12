from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from menu import Menu, MenuItem, create_lazy_menu_callback
from definitions import Student
from menu_students_overview import MenuStudentsOverview
from menu_add_or_edit_student import MenuAddOrEditStudent
from menu_remove_student import MenuRemoveStudent
from menu_create_lesson import MenuCreateLesson
from calendar_manager import ConnectionChecker

class MenuMain(Menu):

    def __init__(self, stdscr, data_base, calendar):
        self.stdscr = stdscr
        self.data_base = data_base
        self.calendar = calendar
        self.items = [MenuItem("Add students", create_lazy_menu_callback(MenuAddOrEditStudent, self.stdscr, self.data_base, action="add", student=Student("---"))),
                    MenuItem("Remove students", create_lazy_menu_callback(MenuRemoveStudent, stdscr, data_base)),
                    MenuItem("Edit students", create_lazy_menu_callback(MenuStudentsOverview, self.stdscr, self.data_base)),
                    MenuItem("Create lesson", create_lazy_menu_callback(MenuCreateLesson, self.stdscr, self.calendar)),
                    MenuItem("Show upcoming events", self.create_list_events_callback()),
                    MenuItem("Exit", None)]
        super().__init__(self.items, self.stdscr)
    
    def create_list_events_callback(self):
        # TODO: Automatically determine the timezone of the computer
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        end_of_two_weeks_from_now = now.replace(hour=0, minute=0, second=0, microsecond=0) 
        end_of_two_weeks_from_now = end_of_two_weeks_from_now + timedelta(days=14, seconds=-1)
        print(f"Period: {now} → {end_of_two_weeks_from_now}")
        def list_events():
            self.stdscr.clear()
            h, w = self.stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
            if ConnectionChecker.is_internet_connection_present():
                events = self.calendar.get_events_in_selected_period(now, end_of_two_weeks_from_now)
                if not events:
                    event_string = f"No events found in the selected period {now.isoformat()} -> {end_of_two_weeks_from_now}"
                    x = w//2 - round(len(event_string)//2)        # Calculate x so text is centered horizontally
                    y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
                    # TODO: Find out why this causes a crash in the .exe variant
                    self.stdscr.addstr(0, 0, event_string)
                else:
                    for index, event in enumerate(events):
                        event_begin = event["start"].get("dateTime", event["start"].get("date"))
                        event_name = event["summary"]
                        event_string = f"{event_name} -> {event_begin}"
                        x = w//2 - len(event_string)//2           # Calculate x so text is centered horizontally
                        y = h//2 - len(events)//2 + index         # Calculate y so the whole menu is vertically centered
                        self.stdscr.addstr(y, x, event_string)
                self.stdscr.refresh()
                self.stdscr.getch()  # Wait for key press before going back
                # return "BACK"   # Return to previous menu
            else:
                error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
                x = w//2 - round(len(error_string)//2)        # Calculate x so text is centered horizontally
                y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
                # TODO: Find out why this causes a crash in the .exe variant
                self.stdscr.addstr(0, 0, error_string)
                self.stdscr.refresh()
                self.stdscr.getch()  # Wait for key press before going back
        return list_events
    