import sqlite3


def init_database():
    """Initialize the SQLite database and tables."""
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    # Create students table
    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id TEXT PRIMARY KEY, name TEXT, course TEXT,
                  attendance REAL, cgpa REAL, semester INTEGER,
                  performance TEXT)''')

    # Create assignments table
    c.execute('''CREATE TABLE IF NOT EXISTS assignments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id TEXT, subject TEXT, score INTEGER,
                  FOREIGN KEY(student_id) REFERENCES students(id))''')

    # Create semester progress table
    c.execute('''CREATE TABLE IF NOT EXISTS semesters
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id TEXT, semester INTEGER, cgpa REAL,
                  FOREIGN KEY(student_id) REFERENCES students(id))''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == '__main__':
    init_database()
