from menu import Menu, create_lazy_menu_callback
from menu_confirm_removal import MenuConfirmRemoval

class MenuRemoveStudent(Menu):
     
    def __init__(self, stdscr, data_base):
        self._data_base = data_base
        super().__init__(stdscr)

    def _refresh_items(self):
        self._items.clear()
        self._items = [Menu.Item(name, create_lazy_menu_callback(MenuConfirmRemoval,
                                                                self._stdscr,
                                                                self._data_base,
                                                                student_name=name,
                                                                refresh_callback=self._refresh_items))
                                                                for (name,) in self._data_base.get_student_names()]
        self._items.append(Menu.Item("Back", self._back_callback()))