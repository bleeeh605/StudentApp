import curses

from menu_main import MenuMain
from database_manager import DatabaseManager
from calendar_manager import CalendarManager
from advance_payment_manager import AdvancePaymentManager

def main(stdscr):
    data_base = DatabaseManager()
    data_base.start()

    calendar = CalendarManager()
    calendar.start()

    advance_payment_manager = AdvancePaymentManager(data_base, calendar)
    advance_payment_manager.do_routine()

    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Main menu
    main_menu = MenuMain(stdscr, data_base, calendar)
    main_menu.run_menu()

# Run the curses application safely (handles terminal cleanup if program crashes)
curses.wrapper(main)
