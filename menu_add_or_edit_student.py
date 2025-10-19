import curses

from menu import Menu
from utility import Student

class MenuAddOrEditStudent(Menu):
     
    def __init__(self, stdscr, data_base, action, student_id=None, student=Student("---"), refresh_callback=None):
        self.stdscr = stdscr
        self.data_base = data_base
        self.student_id = student_id
        self.student = student
        self.action = action
        self.refresh_callback = refresh_callback
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        self.items = [Menu.Item(f"Name: {self.student.name}", self.create_enter_student_parameter_callback("name")),
                Menu.Item(f"Lesson price: {self.student.lesson_price} (€)", self.create_enter_student_parameter_callback("lesson price")),
                Menu.Item(f"Payment in advance: {self.student.advance_payment} (€)", self.create_enter_student_parameter_callback("payment in advance"))]
        if self.action == "add":
            self.items.append(Menu.Item("Confirm", self.create_confirm_add_student_callback()))
        elif self.action == "edit":
            self.items.append(Menu.Item("Confirm", self.create_confirm_edit_student_callback()))
        self.items.append(Menu.Item("Back", self.back_callback()))

    def create_enter_student_parameter_callback(self, option):
        def enter_student_parameter_callback():
            curses.curs_set(1)     # show cursor
            self.stdscr.clear()

            input_str = ""

            while True:
                self.stdscr.clear()
                self.stdscr.addstr(0, 0, f"Type the {option} of the student and press Enter. Press ESC to go back.")
                format_string = ""
                if option == "name":
                    format_string = "Format: [Text] Max. 25 characters."
                elif option == "lesson price":
                    format_string = "Format: [Number] as euro."
                elif option == "payment in advance":
                    format_string = "Format: [Number] as euro."
                self.stdscr.addstr(2, 0, f"{format_string} Current input: " + input_str)

                key = self.stdscr.getch()
                if key == 27:  # ESC to exit
                    break
                elif key in (curses.KEY_ENTER, 10, 13):  # Enter key
                    if input_str.strip():
                        if option == "name":
                            if 0 < len(input_str.strip()) < 25:
                                self.student.name = input_str.strip()
                        elif option == "lesson price":
                            if input_str.strip().isdigit():
                                if 0 <= int(input_str.strip()):
                                    self.student.lesson_price = int(input_str.strip())
                        elif option == "payment in advance":
                            if input_str.strip().isdigit():
                                if 0 <= int(input_str.strip()):
                                    self.student.advance_payment = int(input_str.strip())
                        self.refresh_items()
                        break # Back to previous menu
                elif key == curses.KEY_BACKSPACE or key == 127:
                    input_str = input_str[:-1]
                elif key != -1 and 32 <= key <= 126:  # printable chars
                    input_str += chr(key)
        return enter_student_parameter_callback
    
    def create_confirm_add_student_callback(self):
        def create_confirm_add_student():
            self.data_base.add_student(self.student)
            self.student = Student("---") # Reset the student info for next time when entering the menu
            return "BACK"  # Return to previous menu
        return create_confirm_add_student
    
    def create_confirm_edit_student_callback(self):
        def create_confirm_edit_student_callback():
            self.data_base.edit_student(self.student_id, student=self.student)
            self.refresh_callback()
            return "BACK"  # Return to previous menu
        return create_confirm_edit_student_callback