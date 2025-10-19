from menu import Menu

class MenuConfirmRemoval(Menu):
     
    def __init__(self, stdscr, data_base, student_name, refresh_callback):
        self.stdscr = stdscr
        self.data_base = data_base
        self.student_name = student_name
        self.refresh_callback = refresh_callback
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        self.items = [Menu.Item("Yes", self.create_yes_callback()),
                     Menu.Item("No", self.back_callback()),
                     Menu.Item("Back", self.back_callback())]

    def create_yes_callback(self):
        def yes_callback():
            self.data_base.remove_student(self.student_name)
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"Removed student '{self.student_name}'")
            self.refresh_callback()
            self.stdscr.getch() # Wait for key press before going back
            return "BACK"  # Return to previous menu
        return yes_callback