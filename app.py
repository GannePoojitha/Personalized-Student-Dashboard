from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['DATABASE'] = 'students.db'


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with sample data."""
    conn = get_db_connection()
    # Drop existing tables if they exist
    conn.execute('DROP TABLE IF EXISTS students')
    conn.execute('DROP TABLE IF EXISTS assignments')
    conn.execute('DROP TABLE IF EXISTS semesters')
    conn.execute('DROP TABLE IF EXISTS courses')
    conn.execute('DROP TABLE IF EXISTS attendance')

    # Create tables
    conn.execute('''CREATE TABLE students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        course_id INTEGER,
        performance TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.execute('''CREATE TABLE courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT
    )''')

    conn.execute('''CREATE TABLE assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        subject TEXT NOT NULL,
        score INTEGER NOT NULL,
        max_score INTEGER DEFAULT 100,
        assignment_date DATE,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')

    conn.execute('''CREATE TABLE semesters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        semester INTEGER NOT NULL,
        cgpa REAL NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')

    conn.execute('''CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        date DATE NOT NULL,
        present BOOLEAN DEFAULT 1,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')

    # Insert sample data
    courses = [
        ('B.Tech CSE', 'Computer Science'),
        ('B.Tech IT', 'Information Technology')
    ]
    conn.executemany(
        'INSERT INTO courses (name, department) VALUES (?, ?)',
        courses
    )

    # Insert sample students
    sample_students = [
        (
            'puttu001',
            'Puttu',
            'puttu@example.com',
            '123-456-7890',
            1,
            'Excellent'
        ),
        (
            'arya002',
            'Arya',
            'arya@example.com',
            '123-456-7891',
            2,
            'Very Good'
        ),
        ('rohit003', 'Rohit', 'rohit@example.com', '123-456-7892', 1, 'Good'),
        (
            'priya004',
            'Priya',
            'priya@example.com',
            '123-456-7893',
            2,
            'Excellent'
        )
    ]
    conn.executemany(
        'INSERT INTO students (id, name, email, phone, course_id, performance) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        sample_students
    )
    # Insert sample assignments
    assignments = [
        ('puttu001', 'Math', 90, 100, '2024-01-15'),
        ('puttu001', 'ML', 85, 100, '2024-01-20'),
        ('puttu001', 'Python', 95, 100, '2024-01-25'),
        ('arya002', 'DBMS', 80, 100, '2024-01-15'),
        ('arya002', 'CN', 88, 100, '2024-01-20'),
        ('rohit003', 'Math', 75, 100, '2024-01-15'),
        ('rohit003', 'ML', 92, 100, '2024-01-20'),
        ('priya004', 'DBMS', 94, 100, '2024-01-15'),
        ('priya004', 'CN', 91, 100, '2024-01-20')
    ]
    conn.executemany(
        (
            'INSERT INTO assignments (student_id, subject, score, max_score, '
            'assignment_date) VALUES (?, ?, ?, ?, ?)'
        ),
        assignments
    )

    # Insert semester data
    semesters = [
        ('puttu001', 1, 8.5), ('puttu001', 2, 8.8), ('puttu001', 3, 9.0),
        ('puttu001', 4, 9.1), ('puttu001', 5, 9.2),
        ('arya002', 1, 8.2), ('arya002', 2, 8.5), ('arya002', 3, 8.6),
        ('arya002', 4, 8.7),
        ('rohit003', 1, 7.8), ('rohit003', 2, 8.0), ('rohit003', 3, 8.0),
        ('rohit003', 4, 8.1), ('rohit003', 5, 8.1),
        ('priya004', 1, 9.0), ('priya004', 2, 9.2), ('priya004', 3, 9.3),
        ('priya004', 4, 9.4), ('priya004', 5, 9.4), ('priya004', 6, 9.5)
    ]
    conn.executemany(
        'INSERT INTO semesters (student_id, semester, cgpa) VALUES (?, ?, ?)',
        semesters
    )

    # Insert attendance data (sample for last 30 days)
    import random
    from datetime import timedelta
    students = ['puttu001', 'arya002', 'rohit003', 'priya004']
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        for student_id in students:
            present = random.random() > 0.2  # 80% attendance probability
            conn.execute(
                (
                    'INSERT INTO attendance (student_id, date, present) '
                    'VALUES (?, ?, ?)'
                ),
                (student_id, date, present)
            )

    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/api/students', methods=['GET'])
def get_all_students():
    """Get all students with their details."""
    conn = get_db_connection()
    students = conn.execute('''
        SELECT s.*, c.name as course_name,
               (SELECT AVG(score)
                FROM assignments
                WHERE student_id = s.id) as avg_score,
               (SELECT COUNT(*)
                FROM attendance
                WHERE student_id = s.id AND present = 1) * 100.0 /
               (SELECT COUNT(*)
                FROM attendance
                WHERE student_id = s.id) as attendance_percentage
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
    ''').fetchall()
    result = [dict(student) for student in students]
    conn.close()
    return jsonify(result)


@app.route('/api/student/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get detailed information for a specific student."""
    conn = get_db_connection()
    student = conn.execute('''
        SELECT s.*, c.name as course_name
        FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        WHERE s.id = ?
    ''', (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404
    assignments = conn.execute(
        'SELECT * FROM assignments WHERE student_id = ? ORDER BY assignment_date DESC',
        (student_id,)
    ).fetchall()
    semesters = conn.execute(
        'SELECT * FROM semesters WHERE student_id = ? ORDER BY semester',
        (student_id,)
    ).fetchall()
    attendance = conn.execute(
        '''SELECT date, present FROM attendance
           WHERE student_id = ?
           ORDER BY date DESC LIMIT 30''',
        (student_id,)
    ).fetchall()
    conn.close()
    return jsonify({
        "student": dict(student),
        "assignments": [dict(a) for a in assignments],
        "semesters": [dict(s) for s in semesters],
        "attendance": [dict(a) for a in attendance]
    })


@app.route('/api/student/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student information."""
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE students SET name = ?, email = ?, phone = ?, performance = ? WHERE id = ?',
        (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('performance'),
            student_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Student updated successfully"})


@app.route('/api/assignments', methods=['POST'])
def add_assignment():
    """Add a new assignment for a student."""
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        (
            (
                'INSERT INTO assignments (student_id, subject, score, max_score, '
                'assignment_date) VALUES (?, ?, ?, ?, ?)'
            )
        ),
        (
            data['student_id'],
            data['subject'],
            data['score'],
            data.get('max_score', 100),
            data.get('assignment_date', datetime.now().strftime('%Y-%m-%d'))
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Assignment added successfully"})


@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overall analytics for the dashboard."""
    conn = get_db_connection()
    # Overall statistics
    total_students = (
        conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    )
    avg_cgpa = conn.execute('SELECT AVG(cgpa) FROM semesters').fetchone()[0]
    avg_score_query = 'SELECT AVG(score) FROM assignments'
    avg_score_row = conn.execute(avg_score_query).fetchone()
    avg_attendance = avg_score_row[0]
    # Course distribution
    course_dist = conn.execute('''
        SELECT c.name, COUNT(s.id) as student_count
        FROM courses c
        LEFT JOIN students s ON c.id = s.course_id
        GROUP BY c.name
    ''').fetchall()
    # Recent activity
    recent_assignments = conn.execute('''
        SELECT a.*, s.name as student_name
        FROM assignments a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.assignment_date DESC
        LIMIT 5
    ''').fetchall()
    conn.close()
    return jsonify({
        "overview": {
            "total_students": total_students,
            "average_cgpa": round(avg_cgpa, 2) if avg_cgpa else 0,
            "average_score": round(avg_attendance, 2) if avg_attendance else 0
        },
        "course_distribution": [dict(course) for course in course_dist],
        "recent_activity": [
            dict(assignment) for assignment in recent_assignments
        ]
    })

# ===== ADD THESE NEW ENDPOINTS =====
# ===== ADD THESE ENDPOINTS FOR BUTTON FUNCTIONALITY =====


@app.route('/api/student', methods=['POST'])
def add_student():
    """Add a new student."""
    data = request.get_json()
    print("Adding student:", data)  # Debug log
    
    conn = get_db_connection()
    try:
        conn.execute(
            '''INSERT INTO students (id, name, email, phone, course_id, performance)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (data['id'], data['name'], data.get('email'), data.get('phone'),
             data.get('course_id', 1), data.get('performance', 'Good'))
        )
        conn.commit()
        return jsonify({"message": "Student added successfully"})
    # except sqlite3.IntegrityError as e:
    #     return jsonify({"error": "Student ID already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student."""
    print("Deleting student:", student_id)  # Debug log
    
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        return jsonify({"message": "Student deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close() 


# @app.route('/api/assignments', methods=['POST'])
# def add_assignment():
#     """Add a new assignment for a student."""
#     data = request.get_json()
#     print("Adding assignment:", data)  # Debug log
    
#     conn = get_db_connection()
#     try:
#         conn.execute(
#             '''INSERT INTO assignments (student_id, subject, score, max_score, assignment_date)
#                VALUES (?, ?, ?, ?, ?)''',
#             (data['student_id'], data['subject'], data['score'], 
#              data.get('max_score', 100), data.get('assignment_date', datetime.now().strftime('%Y-%m-%d')))
#         )
#         conn.commit()
#         return jsonify({"message": "Assignment added successfully"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         conn.close()


@app.route('/api/student/<student_id>/attendance', methods=['POST'])
def mark_attendance(student_id):
    """Mark attendance for a student."""
    data = request.get_json()
    print("Marking attendance:", student_id, data)  # Debug log
    
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO attendance (student_id, date, present) VALUES (?, ?, ?)',
            (student_id, data.get('date', datetime.now().strftime('%Y-%m-%d')), data.get('present', True))
        )
        conn.commit()
        return jsonify({"message": "Attendance marked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/search/students', methods=['GET'])
def search_students():
    """Search students by name or ID."""
    query = request.args.get('q', '')
    
    conn = get_db_connection()
    try:
        students = conn.execute('''
            SELECT s.*, c.name as course_name 
            FROM students s 
            LEFT JOIN courses c ON s.course_id = c.id 
            WHERE s.name LIKE ? OR s.id LIKE ?
        ''', (f'%{query}%', f'%{query}%')).fetchall()
        
        result = [dict(student) for student in students]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all available courses."""
    conn = get_db_connection()
    try:
        courses = conn.execute('SELECT * FROM courses').fetchall()
        result = [dict(course) for course in courses]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    # Initialize database on first run
    init_database()
    print("Database initialized with sample data!")
    print("Starting Student Dashboard API...")
    print("Web Interface: http://localhost:5000")
    print("API Base URL: http://localhost:5000/api/students")
    app.run(host='0.0.0.0', port=5000, debug=True)
