import sqlite3

from numpy import void

class Database:
    def __init__(self, database, table):
        self.database = database
        self.table = table
        connection = sqlite3.connect(database, isolation_level=None)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ? (date TEXT, title TEXT, url TEXT, path TEXT)''', (table))

    def save_record(self, date, title, url, path) -> void:
        connection = sqlite3.connect(self.database, isolation_level=None)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO parliament VALUES (?,?,?,?)", (date, title, url, path))

    def record_exists(self, date, title) -> bool:
        connection = sqlite3.connect('parliament.db', isolation_level=None)
        cursor = connection.cursor()
        rows = cursor.execute("SELECT * FROM parliament WHERE date = ? AND title = ?", (date, title))
        return len(rows.fetchall()) > 0