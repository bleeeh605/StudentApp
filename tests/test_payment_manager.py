# pylint: skip-file
import pytest
from unittest.mock import Mock, patch, call

from payment_manager import PaymentManager
from utility import Student

mock_pending_lesson = {
        "id": "sdsdfnojn",
        "summary": "Pavel",
        "colorId": "5",
        "start": {
            "dateTime": "2025-01-15T10:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": "2025-01-15T11:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
    }


mock_paid_lesson = {
        "id": "sdsdfnojn",
        "summary": "Pavel",
        "colorId": "2",
        "start": {
            "dateTime": "2025-01-15T10:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": "2025-01-15T11:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
    }

@pytest.fixture
def test_fixture():
    mock_stdscr = Mock()
    mock_data_base = Mock()
    mock_calendar = Mock()

    return (mock_stdscr, mock_data_base, mock_calendar, PaymentManager(mock_stdscr, mock_data_base, mock_calendar))

def test_do_routine_shows_connecting(test_fixture):
    mock_standard_screen, _, _, payment_manager = test_fixture
    payment_manager._display_unaveilability = Mock()
    mock_standard_screen.getmaxyx.return_value = (24, 80)

    with patch("payment_manager.ConnectionChecker.is_internet_connection_present", return_value=False):
        payment_manager.do_routine()

    mock_standard_screen.clear.assert_called_once()
    mock_standard_screen.getmaxyx.assert_called_once()
    mock_standard_screen.addstr.assert_called_once_with(6, 20, "Connecting...")
    mock_standard_screen.refresh.assert_called_once()

def test_do_routine_shows_unavailability_when_no_connection(test_fixture):
    mock_standard_screen, _, _, payment_manager = test_fixture
    payment_manager._display_unaveilability = Mock()
    mock_standard_screen.getmaxyx.return_value = (24, 80)

    with patch("payment_manager.ConnectionChecker.is_internet_connection_present", return_value=False):
        payment_manager.do_routine()

    payment_manager._display_unaveilability.assert_called_once_with("connection", 20, 6)

def test_do_routine_shows_unavailability_when_no_calendar(test_fixture):
    mock_standard_screen, _, mock_calendar, payment_manager = test_fixture
    payment_manager._display_unaveilability = Mock()
    mock_calendar.service_is_set_up.return_value = False
    mock_standard_screen.getmaxyx.return_value = (24, 80)

    with patch("payment_manager.ConnectionChecker.is_internet_connection_present", return_value=True):
        payment_manager.do_routine()

    payment_manager._display_unaveilability.assert_called_once_with("calendar", 20, 6)

def test_do_routine_shows_update_string_correctly(test_fixture):
    mock_standard_screen, _, mock_calendar, payment_manager = test_fixture
    payment_manager._automatic_student_update = Mock()
    payment_manager._create_updated_students_texts = Mock()
    payment_manager._show_update_text = Mock()
    mock_calendar.service_is_set_up.return_value = True
    mock_standard_screen.getmaxyx.return_value = (24, 80)

    with patch("payment_manager.ConnectionChecker.is_internet_connection_present", return_value=True):
        payment_manager.do_routine()

    mock_standard_screen.addstr.assert_has_calls([
        call(6, 20, "Connecting..."),
        call(6, 20, "Doing an automated update for students. Please wait...")
        ], any_order=False)
    mock_standard_screen.refresh.call_count == 2


def test_automatic_student_update_returns_empty_list_when_data_base_empty(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.get_students_info.return_value = ()

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_calendar.get_student_lessons_in_selected_period.assert_not_called()
    mock_data_base.edit_student.assert_not_called()
    mock_calendar.edit_event.assert_not_called()
    assert updated_students == []

def test_automatic_student_update_skips_paid_lessons(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 120),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_paid_lesson, mock_paid_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_not_called()
    mock_calendar.edit_event.assert_not_called()
    assert updated_students == []

def test_automatic_student_update_skips_demo_lessons(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()
    mock_event_with_color_0 = {
        "id": "sdsdfnojn",
        "summary": "Pavel",
        "colorId": "0",
        "start": {
            "dateTime": "2025-01-15T10:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": "2025-01-15T11:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
    }

    mock_event_with_color_none = {
        "id": "sdsdfnojn",
        "summary": "Pavel",
        "start": {
            "dateTime": "2025-01-15T10:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
        "end": {
            "dateTime": "2025-01-15T11:00:00+01:00",
            "timeZone": "Europe/Berlin",
        },
    }

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 120),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_event_with_color_0, mock_event_with_color_none]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_not_called()
    mock_calendar.edit_event.assert_not_called()
    assert updated_students == []

def test_automatic_student_update_with_student_with_one_lesson(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 120),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_called_once_with(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=60))
    mock_calendar.edit_event.assert_called_once_with(mock_pending_lesson, color_id="2")
    assert updated_students == [("Patrick", mock_pending_lesson, "paid")]

def test_automatic_student_update_with_student_with_three_lessons(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 180),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson, mock_pending_lesson, mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_has_calls([
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=120)),
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=60)),
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=0)),
        ], any_order=False)
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="2"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "paid"),
                                 ("Patrick", mock_pending_lesson, "paid"), 
                                 ("Patrick", mock_pending_lesson, "paid")]

def test_automatic_student_update_with_student_with_one_lesson_and_insufficient_payment(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 40),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_calendar.edit_event.assert_called_once_with(mock_pending_lesson, color_id="11")
    assert updated_students == [("Patrick", mock_pending_lesson, "unpaid")]

def test_automatic_student_update_with_student_with_three_lessons_and_insufficient_payment(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 40),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson, mock_pending_lesson, mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="11"),
        call(mock_pending_lesson, color_id="11"),
        call(mock_pending_lesson, color_id="11"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "unpaid"),
                                ("Patrick", mock_pending_lesson, "unpaid"),
                                ("Patrick", mock_pending_lesson, "unpaid")]

def test_automatic_update_with_student_with_three_lessons_and_insufficient_payment_for_one_of_them(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_calendar.edit_event = Mock()
    mock_data_base.edit_student = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 120),)
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson, mock_pending_lesson, mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_has_calls([
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=60)),
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=0))
        ], any_order=False)
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="11"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "paid"),
                                ("Patrick", mock_pending_lesson, "paid"),
                                ("Patrick", mock_pending_lesson, "unpaid")]

def test_automatic_student_update__with_student_with_two_lessons(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 180), (2, "Divna", 36, 40))
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_has_calls([
        call(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=60)),
        call(student_id=2, student=Student(name="Divna", lesson_price=36, advance_payment=4)),
        ], any_order=False)
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="2"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "paid"),
                                 ("Divna", mock_pending_lesson, "paid")]

def test_automatic_student_update__with_student_with_two_lessons_one_unapid(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 180), (2, "Divna", 36, 0))
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_data_base.edit_student.assert_called_once_with(student_id=1, student=Student(name="Patrick", lesson_price=60, advance_payment=60))
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="2"),
        call(mock_pending_lesson, color_id="11"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "paid"),
                                 ("Divna", mock_pending_lesson, "unpaid")]

def test_automatic_student_update__with_student_with_two_lessons_both_unapid(test_fixture):
    _, mock_data_base, mock_calendar, payment_manager = test_fixture

    mock_data_base.edit_student = Mock()
    mock_calendar.edit_event = Mock()

    mock_data_base.get_students_info.return_value = ((1, "Patrick", 60, 59), (2, "Divna", 36, 35))
    mock_calendar.get_student_lessons_in_selected_period.return_value = [mock_pending_lesson]

    updated_students = payment_manager._automatic_student_update()

    mock_data_base.get_students_info.assert_called_once()
    mock_calendar.edit_event.assert_has_calls([
        call(mock_pending_lesson, color_id="11"),
        call(mock_pending_lesson, color_id="11"),
        ], any_order=True)
    assert updated_students == [("Patrick", mock_pending_lesson, "unpaid"),
                                 ("Divna", mock_pending_lesson, "unpaid")]