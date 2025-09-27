from menu import Menu, MenuItem

class MenuConfirmRemoval(Menu):
     
    def __init__(self, stdscr, data_base, student_name, refresh_callback):
        self.stdscr = stdscr
        self.data_base = data_base
        self.student_name = student_name
        self.refresh_callback = refresh_callback

        items = [MenuItem("Yes", self.create_yes_callback()),
                MenuItem("No", self.back_callback()),
                MenuItem("Back", self.back_callback())]
        super().__init__(items, stdscr)

    def run_menu(self):
        self.stdscr.clear()
        self.stdscr.addstr(2, 2, f"Remove {self.student_name}?")
        self.stdscr.refresh()
        return super().run_menu()

    def create_yes_callback(self):
        def yes_callback():
            self.data_base.remove_student(self.student_name)
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"Removed student '{self.student_name}'")
            self.refresh_callback()
            self.stdscr.getch() # Wait for key press before going back
            return "BACK"  # Return to previous menu
        return yes_callback