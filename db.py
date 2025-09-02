import sqlite3
import hashlib
from datetime import datetime

def connect_db():
    return sqlite3.connect("gym.db")


def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Members
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            start_date TEXT,
            end_date TEXT,
            membership_plan TEXT,
            gender TEXT CHECK(gender IN ('Male','Female','Other')) NOT NULL,
            photo TEXT
        )
    ''')

    # Payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL,
            paid_date TEXT,
            due_date TEXT,
            FOREIGN KEY(member_id) REFERENCES members(id)
        )   
    ''')

    # Attendance
    cursor.execute('DROP TABLE IF EXISTS attendance')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(member_id, date),
            FOREIGN KEY(member_id) REFERENCES members(id)
        )   
    ''')

    # Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )   
    ''')

    # Slots
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            gender TEXT CHECK(gender IN ('Male','Female','Other')) NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS member_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            FOREIGN KEY(member_id) REFERENCES members(id),
            FOREIGN KEY(slot_id) REFERENCES slots(id),
            UNIQUE(member_id, slot_id)
        )
    ''')

    # Trainers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            specialization TEXT,
            status TEXT CHECK(status IN ('Available','Training')) DEFAULT 'Available'
        )
    ''')

    # Trainer Bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainer_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            slot_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            FOREIGN KEY(trainer_id) REFERENCES trainers(id),
            FOREIGN KEY(member_id) REFERENCES members(id),
            FOREIGN KEY(slot_id) REFERENCES slots(id),
            UNIQUE(trainer_id, slot_id, booking_date)
        )
    ''')

    # Insert default admin
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", pw))

    conn.commit()
    conn.close()


# Fetch members with filters and search
def get_members(plan="All", status="All", search=""):
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT id, name, phone, email, address, start_date, end_date, membership_plan, photo FROM members WHERE 1=1"
    params = []

    if plan != "All":
        query += " AND membership_plan=?"
        params.append(plan)

    if status != "All":
        today = datetime.today().strftime("%Y-%m-%d")
        if status == "Active":
            query += " AND end_date>=?"
            params.append(today)
        else:  # Expired
            query += " AND end_date<?"
            params.append(today)

    if search:
        search_like = f"%{search}%"
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
        params.extend([search_like, search_like, search_like])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# Delete member by ID
def delete_member_by_id(member_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")
