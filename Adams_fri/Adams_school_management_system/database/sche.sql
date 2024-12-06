student_management_system/
│
├── app/
│   ├── __init__.py             # Initialize Flask application and extensions
│   ├── __pycache__/            # Python cache files
│   │   ├── __init__.cpython-38.pyc
│   │   ├── models.cpython-38.pyc
│   │   └── routes.cpython-38.pyc
│   ├── config.py               # Configuration settings for the app
│   ├── models.py               # Database models (Student, Fees, etc.)
│   ├── routes.py               # Main application routes (views)
│   ├── static/                 # Static files
│   │   └── css/
│   │       └── styles.css      # Main stylesheet
│   └── templates/
│       ├── New folder/
│       │   ├── 500.html        # Error page
│       │   ├── landing.html    # Landing page for all users
│       │   ├── reset_password.html # Reset password template
│       │   ├── student_login.html  # Student login page
│       │   └── student_portal.html # Student portal page
│       ├── base.html           # Base template
│       ├── landing_page.html   # Initial landing page
│       ├── layout.html         # Layout template for consistent structure
│       ├── secretary/          # Templates specific to secretary role
│       │   ├── edit_student.html
│       │   ├── manage_students.html
│       │   ├── secretary_dashboard.html
│       │   └── student_action.html
│       └── students/           # Templates specific to students
│           ├── reset_password.html
│           ├── student_login.html
│           └── student_portal.html
├── config.py                   # Global configuration
├── migrations/                 # Database migrations (auto-managed by Flask-Migrate)
├── requirements.txt            # Python dependencies
├── run.py                      # Entry point for running the Flask app
├── README.md                   # Project documentation
└── database/
    ├── schema.sql              # SQL script for creating initial database schema
    └── seed_data.sql           # SQL script to seed initial data (e.g., default fees)
