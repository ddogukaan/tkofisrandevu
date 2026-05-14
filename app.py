from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            case_type TEXT NOT NULL,
            summary TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
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
    return render_template("index.html", error=error)

@app.route("/admin")
def admin():
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments ORDER BY date, time")
    appointments = cursor.fetchall()

    conn.close()

    return render_template("admin.html", appointments=appointments)

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)