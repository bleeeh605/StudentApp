from menu import Menu, create_lazy_menu_callback

class MenuRemoveStudent(Menu):
     
    def __init__(self, stdscr, data_base):
        self._data_base = data_base
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        # Create a label for each student in the data base
        self._items = [Menu.Item(name, create_lazy_menu_callback(MenuConfirmRemoval,
                                                                self._stdscr,
                                                                self._data_base,
                                                                student_name=name,
                                                                refresh_callback=self._refresh_items))
                                                                for (name,) in self._data_base.get_student_names()]
        self._items.append(Menu.Item("Back", self._back_callback()))

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
                self._remove_student()
                self._stdscr.clear()
                self._stdscr.addstr(0, 0, f"Removed student '{self._student_name}'")
                self._refresh_callback()
                self._stdscr.getch() # Wait for key press before going back
                return "BACK"  # Return to previous menu
            return yes_callback
            
        def _remove_student(self):
             self._data_base.remove_student(self._student_name)