from menu import Menu

class MenuConfirmRemoval(Menu):
     
    def __init__(self, stdscr, data_base, student_name, refresh_callback):
        self._data_base = data_base
        self._student_name = student_name
        self._refresh_callback = refresh_callback
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item("Yes", self._create_yes_callback()),
                     Menu.Item("No", self._back_callback()),
                     Menu.Item("Back", self._back_callback())]

    def _create_yes_callback(self):
        def yes_callback():
            self._data_base.remove_student(self._student_name)
            self._stdscr.clear()
            self._stdscr.addstr(0, 0, f"Removed student '{self._student_name}'")
            self._refresh_callback()
            self._stdscr.getch() # Wait for key press before going back
            return "BACK"  # Return to previous menu
        return yes_callback