# 🏥 MedTrack – Smart Hospital Asset Management Platform

## 📌 Overview

**MedTrack** is a web-based Smart Hospital Asset Management Platform designed to help hospitals efficiently track and manage medical equipment.

The system provides a centralized dashboard for monitoring equipment status, departments, maintenance schedules, alerts, and maintenance records.

## ✨ Key Features

- 📊 **Interactive Dashboard** – View overall hospital equipment statistics.
- 🏥 **Department Management** – Filter equipment by department.
- 🔍 **Equipment Search** – Search equipment by ID or equipment name.
- 🚦 **Status Tracking** – Monitor Available, Maintenance, and Missing equipment.
- 🔔 **Maintenance Alerts** – Identify upcoming and overdue maintenance.
- 🛠️ **Maintenance Records** – Add and manage equipment maintenance information.
- 👁️ **Equipment Details** – View detailed equipment information.
- ✏️ **Equipment Management** – Add, edit, view, and delete equipment.
- 📈 **Status Analytics** – Visualize equipment status using charts.
- 📄 **PDF Report Generation** – Generate and download hospital equipment reports.
- 🔐 **Admin Login** – Provide administrator access to the management dashboard.

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Charts:** Chart.js
- **PDF Generation:** ReportLab
- **Development Environment:** Visual Studio Code

## 📂 Project Structure

```text
Medtrack/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── screenshots/
│   ├── home.png
│   ├── dashboard.png
│   ├── features.png
│   └── Equipments.png
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