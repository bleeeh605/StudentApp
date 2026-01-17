import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from utility import Student, get_base_path

DATABASE_DIRECTORY = "student_app.db"

class DatabaseManager:

    def __init__(self):
        self._connection = None
        self._cursor = None

        self._migrations = [self._initial_migration, self._migrate_user_settings]

    def start(self) -> None:
        """ Establishes a connection to the data base and initializes the member variables. """

        data_base_path = os.path.join(get_base_path(), DATABASE_DIRECTORY)
        self._connection = sqlite3.connect(data_base_path)
        self._cursor = self._connection.cursor()

    def stop(self) -> None:
        """ Closes the connection to the data base. """

        self._connection.close()

    def _table_exists(self, table_name):
        self._cursor.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type= 'table' AND name = ?
            """, (table_name,))
        return self._cursor.fetchone() is not None

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

    def _get_applied_migration_version(self):
        if not self._table_exists("schema_migrations"):
            return 0
        selection = self._cursor.execute("SELECT migration_version FROM schema_migrations")
        result = selection.fetchone()
        return result[0]
    
    def apply_pending_migrations(self):
        applied_migration_version = self._get_applied_migration_version()
        if applied_migration_version < len(self._migrations):
            new_migration_version = applied_migration_version
            for pending_migration in self._migrations[applied_migration_version:]:
                pending_migration()
                new_migration_version += 1

            query = """INSERT INTO schema_migrations (id, migration_version)
                    VALUES (?, ?)
                    ON CONFLICT(id) 
                    DO UPDATE SET migration_version = excluded.migration_version"""
            self._cursor.execute(query, (1, new_migration_version))
            self._connection.commit()

    def set_budget_start_date(self, new_start_date):
        query = """INSERT INTO user_settings (id, key, value) 
                   VALUES (?, ?, ?) 
                   ON CONFLICT(id)
                   DO UPDATE SET value = excluded.value"""
        self._cursor.execute(query, (1, "budget_start_date", new_start_date))
        self._connection.commit()

    def get_budget_start_date(self):
        selection = self._cursor.execute("""SELECT value
                                         FROM user_settings 
                                         WHERE key='budget_start_date'""")
        result = selection.fetchone()
        return result[0]
    
    def set_budget_end_date(self, new_end_date):
        query = """INSERT INTO user_settings (id, key, value) 
                   VALUES (?, ?, ?) 
                   ON CONFLICT(id)
                   DO UPDATE SET value = excluded.value"""
        self._cursor.execute(query, (2, "budget_end_date", new_end_date))
        self._connection.commit()

    def get_budget_end_date(self):
        selection = self._cursor.execute("""SELECT value
                                         FROM user_settings 
                                         WHERE key='budget_end_date'""")
        result = selection.fetchone()
        return result[0]
    
    # def get_students_with_advance_payment(self): #-> list(tuple)
    #     selection = self.cursor.execute("""SELECT id, name, payment, payment_in_advance
    #                                     FROM students
    #                                     WHERE students.payment_in_advance > 0""")
    #     result = selection.fetchall()
    #     return result


    # MIGRATIONS
    # 1
    def _initial_migration(self):
        self._add_migrations_table()
        self._add_students_table()
        self._add_lessons_table()
        self._add_user_settings_table()
        self._connection.commit()

        if self.get_budget_start_date() is None:
            self.set_budget_start_date(datetime(2025, 10, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")).isoformat())
        if self.get_budget_end_date() is None:
            self.set_budget_end_date(datetime.now(ZoneInfo("UTC")).isoformat())

    def _add_migrations_table(self):
        """ Adds schema_migrations table if it does not exist. """

        self._cursor.execute("""
                        CREATE TABLE IF NOT EXISTS schema_migrations (
                        id INTEGER PRIMARY KEY,
                        migration_version INTEGER
                        )
                        """)
        
    def _add_students_table(self):
        self._cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT,
                payment INTEGER,
                payment_in_advance INTEGER,
                planned_lesson TEXT)
                """)
        
    def _add_lessons_table(self):
        self._cursor.execute("""
                    CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER NOT NULL,
                    date INTEGER,
                    status INTEGER,
                    duration INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(id))
                    """)
        
    def _add_user_settings_table(self):
        """ Add user_settings table if it does not exist. """

        self._cursor.execute("""
                        CREATE TABLE IF NOT EXISTS user_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                        )
                        """)

    # 2
    def _migrate_user_settings(self):
        self._cursor.execute("""
                            CREATE TABLE user_settings_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            key TEXT,
                            value TEXT)
                            """)
        self._cursor.execute("""
                            INSERT INTO user_settings_new 
                            (key, value)
                            SELECT key, value FROM user_settings
                            """)
        self._cursor.execute("DROP TABLE user_settings")
        self._cursor.execute("ALTER TABLE user_settings_new RENAME TO user_settings")
        self._connection.commit()
        