import curses

from menu_main import MenuMain
from database_manager import DatabaseManager
from calendar_manager import CalendarManager
from payment_manager import PaymentManager

from utility import set_terminal_size

def main(standard_screen):
    data_base = DatabaseManager()
    data_base.start()

    data_base.apply_pending_migrations()

    calendar = CalendarManager()
    calendar.start()

    advance_payment_manager = PaymentManager(standard_screen, data_base, calendar)
    advance_payment_manager.do_routine()

    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Main menu
    main_menu = MenuMain(standard_screen, data_base, calendar, update_lessons=advance_payment_manager.do_routine)
    main_menu.run_menu()
    
if __name__ == "__main__":
    set_terminal_size(rows=40, cols=140)
    # Run the curses application safely (handles terminal cleanup if program crashes)
    curses.wrapper(main)
