import sqlite3

if __name__ == "__main__":
    connection = sqlite3.connect("student_app.db")
    cursor = connection.cursor()

    # add students table
    result = cursor.execute("SELECT name FROM sqlite_master WHERE name='students'")
    if result.fetchone() is None:
        cursor.execute("""
                       CREATE TABLE students (
                       id INTEGER PRIMARY KEY,
                       name TEXT,
                       payment INTEGER,
                       payment_in_advance INTEGER,
                       planned_lesson TEXT)
                       """)
        print("Created table 'students'.")

    # add lessons table
    students_table = cursor.execute("SELECT name FROM sqlite_master WHERE name='lessons'")
    if students_table.fetchone() is None:
        cursor.execute("""
                       CREATE TABLE lessons (
                       id INTEGER PRIMARY KEY,
                       student_id INTEGER NOT NULL,
                       date INTEGER,
                       status INTEGER,
                       duration INTEGER,
                       FOREIGN KEY (student_id) REFERENCES students(id))
                       """)
        print("Created table 'lessons'.")

    connection.close()