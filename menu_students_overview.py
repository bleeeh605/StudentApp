import curses

from menu import Menu, create_lazy_menu_callback
from menu_add_or_edit_student import MenuAddOrEditStudent
from utility import Student

class MenuStudentsOverview(Menu):

    def __init__(self, stdscr, data_base):
        self._data_base = data_base
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        student_rows = self._data_base.get_students_info()
        for row in student_rows:
            id, name, lesson_price, advance_payment = row
            student = Student(name, lesson_price, advance_payment)
            self._items.append(Menu.Item(f"{name} | {lesson_price} | {advance_payment}", create_lazy_menu_callback(MenuAddOrEditStudent,
                                                                                                             self._stdscr,
                                                                                                             self._data_base,
                                                                                                             action="edit",
                                                                                                             student_id=id,
                                                                                                             student=student,
                                                                                                             refresh_callback=self._refresh_items)))
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _print_menu(self, selected_row_idx):
        """
        Prints the menu on screen, highlighting the selected row.
        """
        self._stdscr.clear()  # Clear the screen before redrawing
        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window

        longest_label = max([item.label for item in self._items], key=len)
        x = w//2 - len(longest_label)//2  # Calculate x so text is centered horizontally
        y = h//2 - len(self._items)//2 # Calculate y so the whole menu is vertically centered
        self._stdscr.addstr(y, x, "Name | Lesson price (€) | Payment in advance (€)") # print column names as 'title'

        # Loop through each menu item and print it
        for idx, item in enumerate(self._items):
            next_y = y + idx + 1 # + 1 because the 'title' is the first row
            if idx == selected_row_idx: # Highlight the currently selected row (inverted colors)
                self._stdscr.attron(curses.color_pair(1))  # Turn on color pair 1
                self._stdscr.addstr(next_y, x, str(item.label))  # Print the highlighted row
                self._stdscr.attroff(curses.color_pair(1))  # Turn off highlighting
            else: # Print normal (non-highlighted) row
                self._stdscr.addstr(next_y, x, str(item.label))

        self._stdscr.refresh()  # Refresh the screen so changes are visible