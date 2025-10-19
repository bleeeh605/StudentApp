from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from menu import Menu, create_lazy_menu_callback
from utility import Student, ConnectionChecker
from menu_students_overview import MenuStudentsOverview
from menu_add_or_edit_student import MenuAddOrEditStudent
from menu_remove_student import MenuRemoveStudent
from menu_create_lesson import MenuCreateLesson

class MenuMain(Menu):

    def __init__(self, stdscr, data_base, calendar):
        self._data_base = data_base
        self._calendar = calendar
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item("Add students", create_lazy_menu_callback(MenuAddOrEditStudent, self._stdscr, self._data_base, action="add", student=Student("---"))),
                      Menu.Item("Remove students", create_lazy_menu_callback(MenuRemoveStudent, self._stdscr, self._data_base)),
                      Menu.Item("Edit students", create_lazy_menu_callback(MenuStudentsOverview, self._stdscr, self._data_base)),
                      Menu.Item("Create lesson", create_lazy_menu_callback(MenuCreateLesson, self._stdscr, self._calendar)),
                      Menu.Item("Show upcoming events", self._list_events_callback),
                      Menu.Item("Exit", None)]
    
    def _list_events_callback(self):
        # TODO: Automatically determine the timezone of the computer
        now = datetime.now(ZoneInfo("Europe/Berlin"))
        end_of_two_weeks_from_now = now.replace(hour=0, minute=0, second=0, microsecond=0) 
        end_of_two_weeks_from_now = end_of_two_weeks_from_now + timedelta(days=14, seconds=-1)

        self._stdscr.clear()
        if ConnectionChecker.is_internet_connection_present():
            events = self._calendar.get_events_in_selected_period(now, end_of_two_weeks_from_now)
            self._display_events(events, now, end_of_two_weeks_from_now)
        else:
            self._display_connection_unaveilable()

    def _display_events(self, events, start_time, end_time):
        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
        if not events:
            event_string = f"No events found in the selected period {start_time.isoformat()} -> {end_time}"
            x = w//2 - round(len(event_string)//2)        # Calculate x so text is centered horizontally
            y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
            # TODO: Find out why this causes a crash in the .exe variant
            self._stdscr.addstr(0, 0, event_string)
        else:
            for index, event in enumerate(events):
                event_begin = event["start"].get("dateTime", event["start"].get("date"))
                event_name = event["summary"]
                event_string = f"{event_name} -> {event_begin}"
                x = w//2 - len(event_string)//2           # Calculate x so text is centered horizontally
                y = h//2 - len(events)//2 + index         # Calculate y so the whole menu is vertically centered
                self._stdscr.addstr(y, x, event_string)
        self._stdscr.refresh()
        self._stdscr.getch()  # Wait for key press before going back
        # return "BACK"   # Return to previous menu

    def _display_connection_unaveilable(self):
        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window
        error_string = "Connection unavailable. Function is currently disabled. Press any key to continue..."
        x = w//2 - round(len(error_string)//2)        # Calculate x so text is centered horizontally
        y = h//2 - 1                                  # Calculate y so the whole menu is vertically centered
        # TODO: Find out why this causes a crash in the .exe variant
        self._stdscr.addstr(0, 0, error_string)
        self._stdscr.refresh()
        self._stdscr.getch()  # Wait for key press before going back
    