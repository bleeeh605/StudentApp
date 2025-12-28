import sqlite3
import os

from utility import Student, get_base_path

class DatabaseManager:

    def __init__(self):
        self._connection = None
        self._cursor = None

    def start(self) -> None:
        data_base_path = os.path.join(get_base_path(), "student_app.db")
        self._connection = sqlite3.connect(data_base_path)
        self._cursor = self._connection.cursor()

    def stop(self) -> None:
        self._connection.close()

    def add_student(self, student: Student) -> None:
        query = """INSERT INTO students (name, payment, payment_in_advance)
                VALUES (?, ?, ?)"""
        self._cursor.execute(query, (student.name, student.lesson_price, student.advance_payment))
        self._connection.commit()

    def edit_student(self, student_id, student: Student):
        # Find a way to commit only if something really changed?
        query = """UPDATE students
                SET name = ?, payment = ?, payment_in_advance = ?
                WHERE id = ?;
                """
        self._cursor.execute(query, (student.name, student.lesson_price, student.advance_payment, student_id))
        self._connection.commit()

    def remove_student(self, name: str) -> None:
        query = "DELETE FROM students WHERE name = ?;"
        self._cursor.execute(query, (name,))
        self._connection.commit()

    def get_student_names(self): #-> list(tuple)
        selection = self._cursor.execute("SELECT name FROM students")
        result = selection.fetchall()
        return result
    
    def get_students_info(self): #-> list(tuple)
        selection = self._cursor.execute("""SELECT id, name, payment, payment_in_advance
                                        FROM students""")
        result = selection.fetchall()
        return result
    
    def add_settings_table(self):
        """ Add user settings table if it does not exists """
        self._cursor.execute("""
                        CREATE TABLE IF NOT EXISTS user_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                        )
                        """)

    def set_budget_start_date(self, new_start_date):
        query = """INSERT INTO user_settings (key, value) 
                   VALUES (?, ?) 
                   ON CONFLICT(key)
                   DO UPDATE SET value = excluded.value"""
        self._cursor.execute(query, ("budget_start_date", new_start_date))
        self._connection.commit()

    def get_budget_start_date(self):
        selection = self._cursor.execute("""SELECT value
                                         FROM user_settings 
                                         WHERE key='budget_start_date'""")
        result = selection.fetchone()
        return result
    
    def set_budget_end_date(self, new_end_date):
        query = """INSERT INTO user_settings (key, value) 
                   VALUES (?, ?) 
                   ON CONFLICT(key)
                   DO UPDATE SET value = excluded.value"""
        self._cursor.execute(query, ("budget_end_date", new_end_date))
        self._connection.commit()

    def get_budget_end_date(self):
        selection = self._cursor.execute("""SELECT value
                                         FROM user_settings 
                                         WHERE key='budget_end_date'""")
        result = selection.fetchone()
        return result
    
    # def get_students_with_advance_payment(self): #-> list(tuple)
    #     selection = self.cursor.execute("""SELECT id, name, payment, payment_in_advance
    #                                     FROM students
    #                                     WHERE students.payment_in_advance > 0""")
    #     result = selection.fetchall()
    #     return result
        