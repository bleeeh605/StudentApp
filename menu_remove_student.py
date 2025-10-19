from menu import Menu, create_lazy_menu_callback
from menu_confirm_removal import MenuConfirmRemoval

class MenuRemoveStudent(Menu):
     
    def __init__(self, stdscr, data_base):
        self.stdscr = stdscr
        self.data_base = data_base
        super().__init__(stdscr)

    def refresh_items(self):
        self.items.clear()
        self.items = [Menu.Item(name, create_lazy_menu_callback(MenuConfirmRemoval,
                                                                self.stdscr,
                                                                self.data_base,
                                                                student_name=name,
                                                                refresh_callback=self.refresh_items))
                                                                for (name,) in self.data_base.get_student_names()]
        self.items.append(Menu.Item("Back", self.back_callback()))