import curses

from menu import Menu, create_lazy_menu_callback
from menu_add_or_edit_student import MenuAddOrEditStudent
from utility import Student

class MenuStudentsOverview(Menu):

    def __init__(self, stdscr, data_base):
        self.stdscr = stdscr
        self.data_base = data_base
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        student_rows = self.data_base.get_students_info()
        for row in student_rows:
            id, name, lesson_price, advance_payment = row
            student = Student(name, lesson_price, advance_payment)
            self.items.append(Menu.Item(f"{name} | {lesson_price} | {advance_payment}", create_lazy_menu_callback(MenuAddOrEditStudent,
                                                                                                             self.stdscr,
                                                                                                             self.data_base,
                                                                                                             action="edit",
                                                                                                             student_id=id,
                                                                                                             student=student,
                                                                                                             refresh_callback=self.refresh_items)))
        self.items.append(Menu.Item("Back", self.back_callback()))

    def print_menu(self, selected_row_idx):
        """
        Prints the menu on screen, highlighting the selected row.
        """
        self.stdscr.clear()  # Clear the screen before redrawing
        h, w = self.stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window

        longest_label = max([item.label for item in self.items], key=len)
        x = w//2 - len(longest_label)//2  # Calculate x so text is centered horizontally
        y = h//2 - len(self.items)//2 # Calculate y so the whole menu is vertically centered
        self.stdscr.addstr(y, x, "Name | Lesson price (€) | Payment in advance (€)") # print column names as 'title'

        # Loop through each menu item and print it
        for idx, item in enumerate(self.items):
            next_y = y + idx + 1 # + 1 because the 'title' is the first row
            if idx == selected_row_idx: # Highlight the currently selected row (inverted colors)
                self.stdscr.attron(curses.color_pair(1))  # Turn on color pair 1
                self.stdscr.addstr(next_y, x, str(item.label))  # Print the highlighted row
                self.stdscr.attroff(curses.color_pair(1))  # Turn off highlighting
            else: # Print normal (non-highlighted) row
                self.stdscr.addstr(next_y, x, str(item.label))

        self.stdscr.refresh()  # Refresh the screen so changes are visible