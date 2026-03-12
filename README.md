# RailEasy - Railway Concession Portal

A production-ready Flask web application for managing student railway concession applications.

## Key Features

*   **Role-Based Access Control**: Separate views and privileges for Students and Admins.
*   **Secure Authentication**: Passwords hashed using Bcrypt, session management via Flask-Login.
*   **CSRF Protection**: All forms protected against Cross-Site Request Forgery via Flask-WTF.
*   **Document Uploads**: Secure file handling with UUID generation for anonymity and conflict prevention.
*   **Modern Premium UI**: Built with Bootstrap 5, featuring a responsive sidebar, glassmorphism cards, modern hover effects, and a pastel/dark-purple accent theme.

## Setup Instructions

1.  **Virtual Environment**: Ensure you're running this in a safe Python environment.
    ```bash
    cd c:\TEProject\RailEasy
    python -m venv venv
    venv\Scripts\activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Server**:
    The application will automatically initialize the SQLite database on its first run.
    ```bash
    python run.py
    ```

## Admin Access
To simulate an admin user, simply register an account with the email `admin@raileasy.com`. The application routes logic specifically detects this email domain format to escalate privileges to "admin".

## Database Schema (ER Diagram logic)
*   **User Table**:
    Stores both Student and Admin roles via the `role` enum.
    Contains `student_id`, `name`, `email`, password hash, and demographic details (`branch`, `course_class`, `year`, `address`, `nearest_station`).
*   **Application Table**:
    A `One-to-Many` relationship with the `User` table (Each user can submit multiple applications).
    Maintains status enum (`Pending`, `Approved`, `Rejected`), references to uploaded PDF/image file paths, application date, and optional admin remarks.

All database constraints enforce `Foreign Key` cascades naturally via SQLAlchemy. SQLite is used out-of-the-box for portability but can scale to PostgreSQL simply by changing the `.env` `DATABASE_URL`.
