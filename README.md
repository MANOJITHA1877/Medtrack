# 🏥 MedTrack – Smart Hospital Asset Management Platform

## 📌 Overview

**MedTrack** is a web-based Smart Hospital Asset Management Platform designed to help hospitals efficiently track and manage medical equipment.

The system provides a centralized dashboard for monitoring equipment status, departments, maintenance schedules, alerts, and maintenance records.

## ✨ Key Features

* 📊 **Interactive Dashboard** – View overall hospital equipment statistics.
* 🏥 **Department Management** – Filter equipment by department.
* 🔍 **Equipment Search** – Search equipment by ID or name.
* 🚦 **Status Tracking** – Monitor Available, Maintenance, and Missing equipment.
* 🔔 **Maintenance Alerts** – Identify upcoming and overdue maintenance.
* 🛠️ **Maintenance Records** – Add and manage equipment maintenance information.
* 👁️ **Equipment Details** – View detailed information and maintenance history.
* ✏️ **Equipment Management** – Add, edit, view, and delete equipment.
* 📈 **Status Analytics** – Visualize equipment status using charts.
* 📄 **PDF Report Generation** – Generate and download hospital equipment reports.
* 🔐 **Admin Login** – Secure access to the management dashboard.

## 🛠️ Technologies Used

* **Frontend:** HTML, CSS, Bootstrap, JavaScript
* **Backend:** Python, Flask
* **Database:** SQLite
* **Charts:** Chart.js
* **PDF Generation:** ReportLab
* **Development Environment:** Visual Studio Code

## 📂 Project Structure

```text
Medtrack/
│
├── app.py
├── medtrack.db
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── hospital.jpg
│
└── templates/
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── equipment.html
    ├── edit_equipment.html
    ├── equipment_details.html
    ├── contact.html
    └── report.html
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/MANOJITHA1877/Medtrack.git
```

### 2. Open the project folder

```bash
cd Medtrack
```

### 3. Install the required packages

```bash
pip install flask reportlab
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in your browser

```text
http://127.0.0.1:5000
```

## 📊 Dashboard

The dashboard provides:

* Total equipment count
* Available equipment
* Equipment under maintenance
* Missing equipment
* Maintenance alerts
* Equipment status analytics
* Search and filtering
* Equipment management actions

## 📄 Report Generation

MedTrack includes a PDF report generation feature that allows administrators to generate a downloadable report containing hospital equipment information and its maintenance status.

## 🔮 Future Enhancements

* QR-based equipment identification
* Email/SMS maintenance notifications
* Role-based access control
* Cloud database integration
* Mobile-responsive improvements
* Advanced predictive maintenance using machine learning

## 👩‍💻 Author

**Aldini Manojitha**

GitHub: [MANOJITHA1877](https://github.com/MANOJITHA1877)

---

⭐ If you find this project useful, consider giving the repository a star!
