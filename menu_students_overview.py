import curses

from menu import Menu, MenuItem, create_lazy_menu_callback
from menu_add_or_edit_student import MenuAddOrEditStudent
from definitions import Student

class MenuStudentsOverview(Menu):

    def __init__(self, stdscr, data_base):
        self.stdscr = stdscr
        self.data_base = data_base
        self.items = []
        self._needs_refresh = False
        super().__init__(self.items, stdscr)

    def refresh_items(self):
        self.items = []
        student_rows = self.data_base.get_students_info()
        for row in student_rows:
            id, name, lesson_price, advance_payment = row
            student = Student(name, lesson_price, advance_payment)
            self.items.append(MenuItem(f"{name} {lesson_price} {advance_payment}", create_lazy_menu_callback(MenuAddOrEditStudent,
                                                                                                             self.stdscr,
                                                                                                             self.data_base,
                                                                                                             action="edit",
                                                                                                             student_id=id,
                                                                                                             student=student,
                                                                                                             refresh_callback=self.set_refresh_needed_true)))
        self.items.append(MenuItem("Back", self.back_callback()))

    def run_menu(self):
        """
        Runs a given menu and returns the index of the chosen item.
        """
        self.refresh_items()

        current_row = 0  # Start at the first row

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

    def set_refresh_needed_true(self):
        self._needs_refresh = True