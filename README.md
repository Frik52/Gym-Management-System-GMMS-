# 🏋️ Gym Management System

A desktop application built with **PyQt5** and **SQLite** to manage gym operations such as member registration, payments, attendance tracking, trainer assignments, slot management, and report generation.

---

## 📌 Features

- **Login System** – Secure login with admin credentials (default: `admin/admin123`).
- **Dashboard** – Overview of total members, active members, expired memberships, and logo display.
- **Member Management** – Add, edit, and view member information in a tabular format.
- **Payments Management** – Record and view payment history of members.
- **Attendance Tracking** – Mark daily attendance and generate attendance reports.
- **Slots Management** – Assign slots based on gender or preferences.
- **Trainer Management** – Assign trainers to members and track training status.
- **Reports** – Generate member, payment, attendance, and revenue reports.
- **Photo Banner** – Display a banner or motivational photo in the UI.

---

## 📂 Project Structure

├── attendance_report.py # Generates attendance reports
├── attendance_tab.py # Tab for recording attendance
├── dashboard.py # Dashboard view with stats and logo
├── dp.py # Database logic (SQLite)
├── login.py # Login system
├── main.py # Entry point of the application
├── member_form.py # Form to add new members
├── member_table.py # Tabular view of all members
├── payments_tab.py # Payment management tab
├── photo_tab.py # Banner/photo display tab
├── reports_tab.py # Generate reports (member, payment, attendance, revenue)
├── slots_tab.py # Slot allocation tab
├── trainer_tab.py # Trainer assignment tab


---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/gym-management-system.git
cd gym-management-system

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt

python main.py

🔑 Default Credentials
Username: admin
Password: admin123

🛠️ Tech Stack

Frontend/UI: PyQt5

Database: SQLite

Language: Python

👨‍💻 Authors

Md. Saidur Rahman Antu – Developer & Designer

📜 License

This project is licensed under the MIT License
