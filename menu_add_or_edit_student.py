import curses

from menu import Menu, MenuItem
from definitions import Student

class MenuAddOrEditStudent(Menu):
     
    def __init__(self, stdscr, data_base, action, student_id=None, student=Student("---"), refresh_callback=None):
        self.stdscr = stdscr
        self.data_base = data_base
        self.items = []
        self.student_id = student_id
        self.student = student
        self.action = action
        self.refresh_callback = refresh_callback
        self._needs_refresh = False
        super().__init__(self.items, stdscr)

    def refresh_items(self):
        self.items = [MenuItem(f"Name: {self.student.name}", self.create_enter_student_parameter_callback("name")),
                      MenuItem(f"Lesson price: {self.student.lesson_price}", self.create_enter_student_parameter_callback("lesson price")),
                      MenuItem(f"Payment in advance: {self.student.advance_payment}", self.create_enter_student_parameter_callback("payment in advance"))]
        if self.action == "add":
            self.items.append(MenuItem("Confirm", self.create_confirm_add_student_callback()))
        elif self.action == "edit":
            self.items.append(MenuItem("Confirm", self.create_confirm_edit_student_callback()))
        self.items.append(MenuItem("Back", self.back_callback()))

    def create_enter_student_parameter_callback(self, option):
        def create_enter_student_parameter():
            curses.curs_set(1)     # show cursor
            self.stdscr.clear()

            input_str = ""

            while True:
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, f"Type the {option} of the student and press Enter. Press ESC to go back.")
                self.stdscr.addstr(2, 0, "Current input: " + input_str)

                key = self.stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_str.strip():
                        if option == "name":
                            self.student.name = input_str.strip()
                        elif option == "lesson price":
                            if input_str.strip().isdigit():
                                self.student.lesson_price = int(input_str.strip())
                        elif option == "payment in advance":
                            if input_str.strip().isdigit():
                                self.student.advance_payment = int(input_str.strip())
                        self.set_needs_refresh_true()
                        break # Back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_str = input_str[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_str += chr(key)
        return create_enter_student_parameter
    
    def create_confirm_add_student_callback(self):
        def create_confirm_add_student():
            self.data_base.add_student(self.student)
            return "BACK"  # Return to previous menu
        return create_confirm_add_student
    
    def create_confirm_edit_student_callback(self):
        def create_confirm_edit_student_callback():
            self.data_base.edit_student(self.student_id, lesson_price=self.student.lesson_price, payment_in_advance=self.student.advance_payment)
            self.refresh_callback()
            return "BACK"  # Return to previous menu
        return create_confirm_edit_student_callback
    
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