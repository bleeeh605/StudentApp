import sqlite3
import os

from definitions import Student, get_base_path

class DatabaseManager:

    def __init__(self):
        self.connection = None
        self.cursor = None

    def start(self) -> None:
        data_base_path = os.path.join(get_base_path(), "student_app.db")
        self.connection = sqlite3.connect(data_base_path)
        self.cursor = self.connection.cursor()

    def stop(self) -> None:
        self.connection.close()

    def add_student(self, student: Student) -> None:
        self.cursor.execute(f"INSERT INTO students (name, payment, payment_in_advance)"
                            f" VALUES ('{student.name}', {student.lesson_price}, {student.advance_payment})")
        self.connection.commit()

    def edit_student(self, student_id, **kwargs):
        changed = False
        if "lesson_price" in kwargs:
            new_lesson_price = kwargs["lesson_price"]
            self.cursor.execute(f"""UPDATE students
                                SET payment = {new_lesson_price}
                                WHERE id = {student_id}""")
            changed = True
        if "payment_in_advance" in kwargs:
            new_payment_in_advance = kwargs["payment_in_advance"]
            self.cursor.execute(f"""UPDATE students
                                SET payment_in_advance = {new_payment_in_advance}
                                WHERE id = {student_id}""")
            changed = True
        if changed:
            self.connection.commit()

    def remove_student(self, name: str) -> None:
        self.cursor.execute(f"DELETE FROM students WHERE name = '{name}'")
        self.connection.commit()

    def get_student_names(self): #-> list(tuple)
        selection = self.cursor.execute("SELECT name FROM students")
        result = selection.fetchall()
        return result
    
    def get_students_info(self): #-> list(tuple)
        selection = self.cursor.execute("""SELECT id, name, payment, payment_in_advance
                                        FROM students""")
        result = selection.fetchall()
        return result 
    
    def get_students_with_advance_payment(self): #-> list(tuple)
        selection = self.cursor.execute("""SELECT id, name, payment, payment_in_advance
                                        FROM students
                                        WHERE students.payment_in_advance > 0""")
        result = selection.fetchall()
        return result
        