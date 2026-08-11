from flask import Flask, render_template, request, redirect, url_for, session, send_file
from functools import wraps
import sqlite3
from datetime import datetime, date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


app = Flask(__name__)

app.secret_key = "medtrack_secret_key_2026"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    conn = sqlite3.connect("medtrack.db")

    conn.row_factory = sqlite3.Row

    return conn


# ==================================================
# CREATE DATABASE
# ==================================================

def create_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS equipment (

            id TEXT PRIMARY KEY,

            name TEXT NOT NULL,

            department TEXT NOT NULL,

            status TEXT NOT NULL,

            maintenance_date TEXT,

            maintenance_notes TEXT

        )
    """)

    columns = conn.execute(
        "PRAGMA table_info(equipment)"
    ).fetchall()

    column_names = [
        column["name"]
        for column in columns
    ]

    if "maintenance_date" not in column_names:

        conn.execute("""
            ALTER TABLE equipment
            ADD COLUMN maintenance_date TEXT
        """)

    if "maintenance_notes" not in column_names:

        conn.execute("""
            ALTER TABLE equipment
            ADD COLUMN maintenance_notes TEXT
        """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            equipment_id TEXT NOT NULL,

            maintenance_date TEXT NOT NULL,

            maintenance_notes TEXT,

            FOREIGN KEY (equipment_id)
            REFERENCES equipment(id)

        )
    """)

    conn.commit()

    conn.close()


create_database()


# ==================================================
# LOGIN REQUIRED
# ==================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "logged_in" not in session:

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return decorated_function


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        if (
            username == "admin"
            and password == "1234"
        ):

            session["logged_in"] = True

            session["username"] = username

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template(
        "login.html"
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==================================================
# MAINTENANCE ALERTS
# ==================================================

def get_maintenance_alerts(equipment_list):

    alerts = []

    today = date.today()

    for equipment in equipment_list:

        maintenance_date = equipment[
            "maintenance_date"
        ]

        if not maintenance_date:
            continue

        try:

            maintenance_day = datetime.strptime(
                maintenance_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            continue

        days_difference = (
            maintenance_day - today
        ).days

        # OVERDUE

        if days_difference < 0:

            alerts.append({

                "equipment_id":
                    equipment["id"],

                "equipment_name":
                    equipment["name"],

                "department":
                    equipment["department"],

                "maintenance_date":
                    maintenance_date,

                "days":
                    abs(days_difference),

                "type":
                    "overdue",

                "message":
                    f"Maintenance overdue by "
                    f"{abs(days_difference)} day(s)."

            })

        # TODAY

        elif days_difference == 0:

            alerts.append({

                "equipment_id":
                    equipment["id"],

                "equipment_name":
                    equipment["name"],

                "department":
                    equipment["department"],

                "maintenance_date":
                    maintenance_date,

                "days":
                    0,

                "type":
                    "today",

                "message":
                    "Maintenance is due today."

            })

        # WITHIN 7 DAYS

        elif days_difference <= 7:

            alerts.append({

                "equipment_id":
                    equipment["id"],

                "equipment_name":
                    equipment["name"],

                "department":
                    equipment["department"],

                "maintenance_date":
                    maintenance_date,

                "days":
                    days_difference,

                "type":
                    "soon",

                "message":
                    f"Maintenance due in "
                    f"{days_difference} day(s)."

            })

    return alerts


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db_connection()

    equipment_list = conn.execute("""
        SELECT *
        FROM equipment
        ORDER BY id
    """).fetchall()

    conn.close()

    maintenance_alerts = get_maintenance_alerts(
        equipment_list
    )

    overdue_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "overdue"
    )

    today_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "today"
    )

    soon_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "soon"
    )

    return render_template(
        "dashboard.html",

        equipment_list=equipment_list,

        maintenance_alerts=
            maintenance_alerts,

        overdue_count=
            overdue_count,

        today_count=
            today_count,

        soon_count=
            soon_count,

        total_alerts=
            len(maintenance_alerts)
    )


# ==================================================
# REPORT PAGE
# ==================================================

@app.route("/report")
@login_required
def report():

    conn = get_db_connection()

    equipment_list = conn.execute("""
        SELECT *
        FROM equipment
        ORDER BY id
    """).fetchall()

    maintenance_history = conn.execute("""
        SELECT

            maintenance_history.*,

            equipment.name AS equipment_name

        FROM maintenance_history

        LEFT JOIN equipment

        ON maintenance_history.equipment_id
           = equipment.id

        ORDER BY maintenance_date DESC

    """).fetchall()

    conn.close()

    maintenance_alerts = get_maintenance_alerts(
        equipment_list
    )

    total_equipment = len(
        equipment_list
    )

    available_count = sum(
        1
        for equipment in equipment_list
        if equipment["status"] == "Available"
    )

    maintenance_count = sum(
        1
        for equipment in equipment_list
        if equipment["status"] == "Maintenance"
    )

    missing_count = sum(
        1
        for equipment in equipment_list
        if equipment["status"] == "Missing"
    )

    overdue_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "overdue"
    )

    today_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "today"
    )

    soon_count = sum(
        1
        for alert in maintenance_alerts
        if alert["type"] == "soon"
    )

    return render_template(

        "report.html",

        equipment_list=equipment_list,

        maintenance_history=
            maintenance_history,

        maintenance_alerts=
            maintenance_alerts,

        total_equipment=
            total_equipment,

        available_count=
            available_count,

        maintenance_count=
            maintenance_count,

        missing_count=
            missing_count,

        overdue_count=
            overdue_count,

        today_count=
            today_count,

        soon_count=
            soon_count,

        report_date=
            datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
    )


# ==================================================
# DOWNLOAD REPORT AS PDF
# ==================================================

@app.route("/download_report")
@login_required
def download_report():

    conn = get_db_connection()

    equipment_list = conn.execute("""
        SELECT *
        FROM equipment
        ORDER BY id
    """).fetchall()

    maintenance_history = conn.execute("""
        SELECT

            maintenance_history.*,

            equipment.name AS equipment_name

        FROM maintenance_history

        LEFT JOIN equipment

        ON maintenance_history.equipment_id
           = equipment.id

        ORDER BY maintenance_date DESC

    """).fetchall()

    conn.close()

    maintenance_alerts = get_maintenance_alerts(
        equipment_list
    )

    # COUNTS

    total_equipment = len(
        equipment_list
    )

    available_count = sum(
        1
        for e in equipment_list
        if e["status"] == "Available"
    )

    maintenance_count = sum(
        1
        for e in equipment_list
        if e["status"] == "Maintenance"
    )

    missing_count = sum(
        1
        for e in equipment_list
        if e["status"] == "Missing"
    )

    overdue_count = sum(
        1
        for a in maintenance_alerts
        if a["type"] == "overdue"
    )

    today_count = sum(
        1
        for a in maintenance_alerts
        if a["type"] == "today"
    )

    soon_count = sum(
        1
        for a in maintenance_alerts
        if a["type"] == "soon"
    )

    # PDF BUFFER

    buffer = BytesIO()

    document = SimpleDocTemplate(

        buffer,

        pagesize=landscape(A4),

        rightMargin=30,

        leftMargin=30,

        topMargin=30,

        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]

    normal_style = styles["BodyText"]

    story = []

    # ------------------------------------------------
    # TITLE
    # ------------------------------------------------

    story.append(
        Paragraph(
            "MedTrack",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Smart Hospital Asset Management Report",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Generated on: "
            +
            datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),
            normal_style
        )
    )

    story.append(
        Spacer(1, 20)
    )

    # ------------------------------------------------
    # EQUIPMENT SUMMARY
    # ------------------------------------------------

    story.append(
        Paragraph(
            "Equipment Summary",
            heading_style
        )
    )

    summary_data = [

        [
            "Total Equipment",
            "Available",
            "Maintenance",
            "Missing"
        ],

        [
            str(total_equipment),
            str(available_count),
            str(maintenance_count),
            str(missing_count)
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            140,
            140,
            140,
            140
        ]
    )

    summary_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0d6efd")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 20)
    )

    # ------------------------------------------------
    # MAINTENANCE ALERT SUMMARY
    # ------------------------------------------------

    story.append(
        Paragraph(
            "Maintenance Alert Summary",
            heading_style
        )
    )

    alert_data = [

        [
            "Overdue",
            "Due Today",
            "Due Within 7 Days"
        ],

        [
            str(overdue_count),
            str(today_count),
            str(soon_count)
        ]

    ]

    alert_table = Table(
        alert_data,
        colWidths=[
            180,
            180,
            180
        ]
    )

    alert_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#ffc107")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            )

        ])
    )

    story.append(alert_table)

    story.append(
        Spacer(1, 25)
    )

    # ------------------------------------------------
    # EQUIPMENT DETAILS
    # ------------------------------------------------

    story.append(
        Paragraph(
            "Equipment Details",
            heading_style
        )
    )

    equipment_data = [

        [
            "ID",
            "Equipment",
            "Department",
            "Status",
            "Maintenance Date",
            "Notes"
        ]

    ]

    for equipment in equipment_list:

        equipment_data.append([

            str(equipment["id"]),

            str(equipment["name"]),

            str(equipment["department"]),

            str(equipment["status"]),

            str(
                equipment["maintenance_date"]
                or "Not scheduled"
            ),

            str(
                equipment["maintenance_notes"]
                or "-"
            )

        ])

    equipment_table = Table(

        equipment_data,

        repeatRows=1,

        colWidths=[

            50,

            120,

            100,

            80,

            110,

            180
        ]
    )

    equipment_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0d6efd")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#f2f6fa")
                ]
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )

        ])
    )

    story.append(
        equipment_table
    )

    story.append(
        Spacer(1, 25)
    )

    # ------------------------------------------------
    # MAINTENANCE HISTORY
    # ------------------------------------------------

    story.append(
        Paragraph(
            "Maintenance History",
            heading_style
        )
    )

    if maintenance_history:

        history_data = [

            [
                "#",
                "Equipment",
                "Equipment ID",
                "Date",
                "Notes"
            ]

        ]

        for index, record in enumerate(
            maintenance_history,
            start=1
        ):

            history_data.append([

                str(index),

                str(
                    record["equipment_name"]
                    or "Unknown"
                ),

                str(
                    record["equipment_id"]
                ),

                str(
                    record["maintenance_date"]
                ),

                str(
                    record["maintenance_notes"]
                    or "-"
                )

            ])

        history_table = Table(

            history_data,

            repeatRows=1,

            colWidths=[

                40,

                150,

                100,

                100,

                250
            ]
        )

        history_table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0d6efd")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f2f6fa")
                    ]
                )

            ])
        )

        story.append(
            history_table
        )

    else:

        story.append(
            Paragraph(
                "No maintenance history available.",
                normal_style
            )
        )

    story.append(
        Spacer(1, 25)
    )

    story.append(
        Paragraph(
            "MedTrack | Smart Hospital Asset Tracking System",
            normal_style
        )
    )

    # ------------------------------------------------
    # BUILD PDF
    # ------------------------------------------------

    document.build(story)

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="MedTrack_Report.pdf",

        mimetype="application/pdf"
    )


# ==================================================
# ADD EQUIPMENT
# ==================================================

@app.route(
    "/equipment",
    methods=["GET", "POST"]
)
@login_required
def equipment():

    if request.method == "POST":

        equipment_id = request.form.get(
            "equipment_id"
        )

        equipment_name = request.form.get(
            "equipment_name"
        )

        department = request.form.get(
            "department"
        )

        status = request.form.get(
            "status"
        )

        maintenance_date = request.form.get(
            "maintenance_date",
            ""
        )

        maintenance_notes = request.form.get(
            "maintenance_notes",
            ""
        )

        conn = get_db_connection()

        try:

            conn.execute("""
                INSERT INTO equipment

                (
                    id,
                    name,
                    department,
                    status,
                    maintenance_date,
                    maintenance_notes
                )

                VALUES (?, ?, ?, ?, ?, ?)

            """, (

                equipment_id,

                equipment_name,

                department,

                status,

                maintenance_date,

                maintenance_notes

            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Equipment ID already exists!"

        conn.close()

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "equipment.html"
    )


# ==================================================
# EDIT EQUIPMENT
# ==================================================

@app.route(
    "/edit_equipment/<equipment_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_equipment(equipment_id):

    conn = get_db_connection()

    equipment = conn.execute("""
        SELECT *
        FROM equipment
        WHERE id = ?
    """, (equipment_id,)).fetchone()

    if equipment is None:

        conn.close()

        return "Equipment not found"

    if request.method == "POST":

        equipment_name = request.form.get(
            "equipment_name"
        )

        department = request.form.get(
            "department"
        )

        status = request.form.get(
            "status"
        )

        maintenance_date = request.form.get(
            "maintenance_date",
            ""
        )

        maintenance_notes = request.form.get(
            "maintenance_notes",
            ""
        )

        conn.execute("""
            UPDATE equipment

            SET

                name = ?,

                department = ?,

                status = ?,

                maintenance_date = ?,

                maintenance_notes = ?

            WHERE id = ?

        """, (

            equipment_name,

            department,

            status,

            maintenance_date,

            maintenance_notes,

            equipment_id

        ))

        conn.commit()

        conn.close()

        return redirect(
            url_for("dashboard")
        )

    conn.close()

    return render_template(
        "edit_equipment.html",
        equipment=equipment
    )


# ==================================================
# EQUIPMENT DETAILS
# ==================================================

@app.route(
    "/equipment_details/<equipment_id>"
)
@login_required
def equipment_details(equipment_id):

    conn = get_db_connection()

    equipment = conn.execute("""
        SELECT *
        FROM equipment
        WHERE id = ?
    """, (equipment_id,)).fetchone()

    if equipment is None:

        conn.close()

        return "Equipment not found"

    history = conn.execute("""
        SELECT *
        FROM maintenance_history

        WHERE equipment_id = ?

        ORDER BY maintenance_date DESC

    """, (equipment_id,)).fetchall()

    conn.close()

    return render_template(

        "equipment_details.html",

        equipment=equipment,

        history=history
    )


# ==================================================
# ADD MAINTENANCE
# ==================================================

@app.route(
    "/add_maintenance/<equipment_id>",
    methods=["POST"]
)
@login_required
def add_maintenance(equipment_id):

    maintenance_date = request.form.get(
        "maintenance_date"
    )

    maintenance_notes = request.form.get(
        "maintenance_notes"
    )

    conn = get_db_connection()

    equipment = conn.execute("""
        SELECT id
        FROM equipment
        WHERE id = ?
    """, (equipment_id,)).fetchone()

    if equipment is None:

        conn.close()

        return "Equipment not found"

    conn.execute("""
        INSERT INTO maintenance_history

        (
            equipment_id,
            maintenance_date,
            maintenance_notes
        )

        VALUES (?, ?, ?)

    """, (

        equipment_id,

        maintenance_date,

        maintenance_notes

    ))

    conn.commit()

    conn.close()

    return redirect(
        url_for(
            "equipment_details",
            equipment_id=equipment_id
        )
    )


# ==================================================
# DELETE EQUIPMENT
# ==================================================

@app.route(
    "/delete_equipment/<equipment_id>"
)
@login_required
def delete_equipment(equipment_id):

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM maintenance_history
        WHERE equipment_id = ?
    """, (equipment_id,))

    conn.execute("""
        DELETE FROM equipment
        WHERE id = ?
    """, (equipment_id,))

    conn.commit()

    conn.close()

    return redirect(
        url_for("dashboard")
    )


# ==================================================
# CONTACT
# ==================================================

@app.route("/contact")
def contact():

    return render_template(
        "contact.html"
    )


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )