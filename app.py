from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "turan_karakoc_super_secret_2026"

ADMIN_USERNAME = "turankarakoc"
ADMIN_PASSWORD = "123456"


def init_db():
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            case_type TEXT NOT NULL,
            summary TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def generate_slots():
    slots = []
    current = datetime.strptime("10:00", "%H:%M")
    end = datetime.strptime("17:00", "%H:%M")

    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)

    return slots


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    error = None

    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        case_type = request.form["case_type"]
        summary = request.form["summary"]
        date = request.form["date"]
        time = request.form["time"]

        if not summary.strip():
            error = "Hukuki olay özeti zorunludur."
        else:
            chosen_date = datetime.strptime(date, "%Y-%m-%d")

            if chosen_date.weekday() in [5, 6]:
                error = "Hafta sonu randevu alınamaz."
            else:
                cursor.execute(
                    "SELECT * FROM appointments WHERE date=? AND time=?",
                    (date, time)
                )

                if cursor.fetchone():
                    error = "Bu saat dolu."
                else:
                    cursor.execute("""
                        INSERT INTO appointments
                        (name, phone, case_type, summary, date, time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, phone, case_type, summary, date, time))

                    conn.commit()

    conn.close()
    return render_template("appointment.html", error=error)


@app.route("/available-slots")
def available_slots():
    date = request.args.get("date")

    if not date:
        return jsonify([])

    chosen_date = datetime.strptime(date, "%Y-%m-%d")

    if chosen_date.weekday() in [5, 6]:
        return jsonify([])

    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("SELECT time FROM appointments WHERE date=?", (date,))
    booked = [row[0] for row in cursor.fetchall()]

    conn.close()

    slots = generate_slots()

    result = []

    for slot in slots:
        result.append({
            "time": slot,
            "available": slot not in booked
        })

    return jsonify(result)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        else:
            error = "Hatalı giriş."

    return render_template("login.html", error=error)


@app.route("/client-login")
def client_login():
    return "<h1>Müvekkil paneli yakında eklenecek.</h1>"


@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments ORDER BY date, time")
    appointments = cursor.fetchall()

    conn.close()

    return render_template("admin.html", appointments=appointments)


@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)