import curses

class Menu:

    class Item():
        def __init__(self, label, callback=None):
            self.label = label          # What’s shown in the menu
            self.callback = callback    # Function to call when selected

    def __init__(self, stdscr) -> None:
        self._stdscr = stdscr
        self._items = []

    def run_menu(self):
        """
        Runs a given menu and returns the index of the chosen item.
        """
        current_row = 0  # Start at the first row
        self._refresh_items() # Update and show menu items

        while True:

            self._print_menu(current_row) # Draw menu

            key = self._stdscr.getch() # Wait for the next key press
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(self._items)-1:
                current_row += 1
            elif key in [curses.KEY_ENTER, 10, 13]: # Current row was selected!
                action = self._items[current_row].callback
                if action:
                    result = action() # Call callback
                    if result == "BACK":
                        break
                else:
                    break

            # Redraw menu with updated selection
            self._print_menu(current_row)


    def _print_menu(self, selected_row_idx):
        """
        Prints a given menu on screen, highlighting the selected row.
        """
        self._stdscr.clear()  # Clear the screen before redrawing
        h, w = self._stdscr.getmaxyx()  # Get the height (h) and width (w) of the terminal window

        # Loop through each menu item and print it
        for idx, item in enumerate(self._items):
            x = w//2 - len(str(item.label))//2  # Calculate x so text is centered horizontally
            y = h//2 - len(self._items)//2 + idx  # Calculate y so the whole menu is vertically centered

            if idx == selected_row_idx: # Highlight the currently selected row (inverted colors)
                self._stdscr.attron(curses.color_pair(1))  # Turn on color pair 1
                self._stdscr.addstr(y, x, str(item.label))  # Print the highlighted row
                self._stdscr.attroff(curses.color_pair(1))  # Turn off highlighting
            else: # Print normal (non-highlighted) row
                self._stdscr.addstr(y, x, str(item.label))

        self._stdscr.refresh()  # Refresh the screen so changes are visible

    def _refresh_items(self):
        return

    def _back_callback(self):
        def back():
            return "BACK"
        return back

def create_lazy_menu_callback(menu: Menu, stdscr, data_base, *args, **kwargs):
    def create_menu():
        new_menu = menu(stdscr, data_base, *args, **kwargs)
        new_menu.run_menu()
    return create_menu