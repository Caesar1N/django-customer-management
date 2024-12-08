# Django Customer Management App

This is a **Django-based Customer Management Application** designed to streamline customer data handling, schedule messages, and manage invoice receipts. It integrates a responsive UI with modern backend features.

---

## **Features**

- Add and manage customer information.
- Upload and manage invoices (supports PDF and image formats; converts images to PDF).
- Schedule WhatsApp or SMS messages for customers.
- Set and view reminders for scheduled messages.
- Dynamically loaded modals for adding/editing customers, invoices, and scheduling messages.
- Seamless form submissions using AJAX.

---

## **Tech Stack**

- **Backend**: Django 4.0
- **Frontend**: Bootstrap 4, jQuery
- **Database**: SQLite (default for development)
- **Task Queue** (Planned): Celery for background tasks
- **Dependencies**:
  - `Django Bootstrap Datepicker Plus`
  - `Pillow`
  - `Moment.js`

---

## **Installation**

### Prerequisites
- Python 3.8+
- Virtual Environment tool (`venv` or `virtualenv`)
- Git

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Caesar1N/django-customer-management.git
   cd django-customer-management

2. Create a virtual environment and activate it:
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

    pip install -r requirements.txt

4. Apply migrations:

    python manage.py migrate

5. Run the development server:

    python manage.py runserver

6. Open the app in your browser:

    http://127.0.0.1:8000
    
### USAGE


1. Customer Management
Add, edit, or delete customers from the interface.
View detailed information about each customer.
2. Invoice Management
Upload receipts in PDF, PNG, or JPEG format.
Images are automatically converted to PDFs.
3. Message Scheduling
Schedule WhatsApp or SMS messages.
View and manage reminders for upcoming messages.

### Folder Structure

django-customer-management/
├── cus/
│   ├── customer_manager/
│   │   ├── crm/
│   │   ├── customer_manager/
│   │   ├── db.sqlite3
│   │   ├── manage.py
│   │   ├── media/
│   │   ├── static/
│   │   └── ...
│   └── context.txt
├── venv/
└── ...

### Contributing 

Contributions are welcome! Please follow these steps:

1. Fork the repository.

2. Create a feature branch:
    git checkout -b feature/your-feature-name

3. Commit your changes:
    git commit -m "Add a meaningful commit message"

4. Push to the branch:
    git push origin feature/your-feature-name

5. Create a pull request.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

### Acknowledgements
Django
Bootstrap
jQuery
Moment.js
