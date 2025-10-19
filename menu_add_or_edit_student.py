import curses

from menu import Menu
from utility import Student

class MenuAddOrEditStudent(Menu):
     
    def __init__(self, stdscr, data_base, action, student_id=None, student=Student("---"), refresh_callback=None):
        self._data_base = data_base
        self._student_id = student_id
        self._student = student
        self._action = action
        self._refresh_callback = refresh_callback
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item(f"Name: {self._student.name}", self._create_enter_student_parameter_callback("name")),
                Menu.Item(f"Lesson price: {self._student.lesson_price} (€)", self._create_enter_student_parameter_callback("lesson price")),
                Menu.Item(f"Payment in advance: {self._student.advance_payment} (€)", self._create_enter_student_parameter_callback("payment in advance"))]
        if self._action == "add":
            self._items.append(Menu.Item("Confirm", self._create_confirm_add_student_callback()))
        elif self._action == "edit":
            self._items.append(Menu.Item("Confirm", self._create_confirm_edit_student_callback()))
        self._items.append(Menu.Item("Back", self._back_callback()))

    def _create_enter_student_parameter_callback(self, option):
        def enter_student_parameter_callback():
            curses.curs_set(1)     # show cursor
            self._stdscr.clear()

            input_str = ""

            while True:
                self._stdscr.clear()
                self._stdscr.addstr(0, 0, f"Type the {option} of the student and press Enter. Press ESC to go back.")
                format_string = ""
                if option == "name":
                    format_string = "Format: [Text] Max. 25 characters."
                elif option == "lesson price":
                    format_string = "Format: [Number] as euro."
                elif option == "payment in advance":
                    format_string = "Format: [Number] as euro."
                self._stdscr.addstr(2, 0, f"{format_string} Current input: " + input_str)

                key = self._stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_str.strip():
                        if option == "name":
                            if 0 < len(input_str.strip()) < 25:
                                self._student.name = input_str.strip()
                        elif option == "lesson price":
                            if input_str.strip().isdigit():
                                if 0 <= int(input_str.strip()):
                                    self._student.lesson_price = int(input_str.strip())
                        elif option == "payment in advance":
                            if input_str.strip().isdigit():
                                if 0 <= int(input_str.strip()):
                                    self._student.advance_payment = int(input_str.strip())
                        self._refresh_items()
                        break # Back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_str = input_str[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_str += chr(key)
        return enter_student_parameter_callback
    
    def _create_confirm_add_student_callback(self):
        def create_confirm_add_student():
            self._data_base.add_student(self._student)
            self._student = Student("---") # Reset the student info for next time when entering the menu
            return "BACK"  # Return to previous menu
        return create_confirm_add_student
    
    def _create_confirm_edit_student_callback(self):
        def create_confirm_edit_student_callback():
            self._data_base.edit_student(self._student_id, student=self._student)
            self._refresh_callback()
            return "BACK"  # Return to previous menu
        return create_confirm_edit_student_callback