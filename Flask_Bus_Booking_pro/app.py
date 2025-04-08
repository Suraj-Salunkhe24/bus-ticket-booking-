import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.utils import secure_filename
import stripe

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["UPLOAD_FOLDER"] = "D:/class file/1_Domain_Python/python_programs/Flask_Bus_Booking_pro/static/assets/images"
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = 1800  # 30 minutes

stripe.api_key = "your_stripe_secret_key_here"  # Replace with your Stripe secret key

# Database initialization
def init_db():
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS passenger_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                From_Location TEXT NOT NULL,
                To_Location TEXT NOT NULL,
                Departure TEXT NOT NULL,
                Arrival TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS travels_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                "Travels Name" TEXT NOT NULL,
                "Vehicle Number" TEXT NOT NULL,
                "Front Image" TEXT NOT NULL,
                "Inside Image" TEXT NOT NULL,
                Available_Scats INTEGER NOT NULL,
                From_Location TEXT NOT NULL,
                To_Location TEXT NOT NULL,
                Amount REAL NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_information (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mobile_no TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        con.commit()

init_db()

@app.route("/")
def home():
    locations = ["PUNE", "MUMBAI", "SATARA", "SANGLI", "KOLHAPUR", "SOLAPUR", "MIRAJ", "SANGOLA"]
    return render_template("home.html", locations=locations)

@app.route("/user_data", methods=["POST"])
def user_data():
    if request.method == "POST":
        st = request.form.get("star_location")
        ed = request.form.get("end_location")
        de = request.form.get("Departure")
        re = request.form.get("Arrival")

        if not st or not ed or not de or not re:
            flash("All fields are required. Please fill in all fields.", "error")
            return redirect(url_for("home"))

        if st == ed:
            flash("From and To locations cannot be the same.", "error")
            return redirect(url_for("home"))

        try:
            with sqlite3.connect("passenger.db") as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO passenger_data (From_Location, To_Location, Departure, Arrival)
                    VALUES (?, ?, ?, ?)
                """, (st, ed, de, re))
                con.commit()
            session["session_name"] = st
            return redirect(url_for("Travels_data"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("home"))

@app.route("/data", methods=["GET"])
def data():
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM passenger_data ORDER BY id DESC")
        info = cur.fetchall()
    return render_template("by_user_data.html", info=info)

@app.route("/Travel_roots", methods=["POST"])
def Travel_roots():
    if request.method == "POST":
        return redirect(url_for("data"))

@app.route("/addmin_login")
def addmin_login():
    return render_template("addmin_login.html")




admin_email = "surajsalunkhe2424@gmail.com"            # admin Email And Password
admin_password = "1551"

@app.route("/admin_log", methods=["POST"])
def admin_log():
    if request.method == "POST":
        na = request.form["email"]
        pa = request.form["password"]

        if na == admin_email and pa == admin_password:
            session["session_password"] = pa
            return redirect(url_for("admin_main"))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for("addmin_login"))

@app.route("/admin_main")
def admin_main():
    if session.get("session_password") is not None:
        return render_template("admin_main_page.html")
    return redirect(url_for("addmin_login"))

@app.route("/travels", methods=["POST", "GET"])
def travels():
    return render_template("travles_add_page.html")

@app.route("/Travel_details", methods=["POST", "GET"])
def Travel_details():
    if request.method == "POST":
        ta = request.form["Travels_name"]
        vn = request.form["Vehicle_Number"]
        Front_Image = request.files["Front_Image"]
        Inside_Image = request.files["Inside_Image"]
        avs = request.form["Available_Seats"]
        form = request.form["From"]
        to = request.form["To"]
        am = request.form["Amount"]

        try:
            with sqlite3.connect("passenger.db") as con:
                cur = con.cursor()
                front_image_filename = secure_filename(Front_Image.filename)
                inside_image_filename = secure_filename(Inside_Image.filename)
                Front_Image.save(os.path.join(app.config["UPLOAD_FOLDER"], front_image_filename))
                Inside_Image.save(os.path.join(app.config["UPLOAD_FOLDER"], inside_image_filename))

                cur.execute("""
                    INSERT INTO travels_info ("Travels Name", "Vehicle Number", "Front Image", "Inside Image", Available_Scats, From_Location, To_Location, Amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ta, vn, front_image_filename, inside_image_filename, avs, form, to, am))
                con.commit()
            return redirect(url_for("Travels_data"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("travels"))

@app.route("/Travels_data", methods=["GET", "POST"])
def Travels_data():
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM travels_info")
        data = cur.fetchall()
    return render_template("travels_info.html", data=data)

@app.route("/update_seat/<int:travel_id>", methods=["POST"])
def update_seat(travel_id):
    available_seats = request.form.get("available_seats")

    if available_seats is not None:
        try:
            with sqlite3.connect("passenger.db") as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE travels_info
                    SET Available_Scats = ?
                    WHERE id = ?
                """, (available_seats, travel_id))
                con.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        return jsonify({"success": False, "error": "No available seats provided"})

@app.route("/Travel_ADD_view", methods=["POST"])
def Travel_ADD_view():
    if request.method == "POST":
        return redirect(url_for("travels"))

@app.route("/Travel_view", methods=["GET"])
def Travel_view():
    if request.method == "GET":
        return redirect(url_for("Travels_data"))

@app.route("/user_main", methods=["GET"])
def user_travel_view_btn():
    session.pop("session_password", None)
    return redirect(url_for("Travels_data"))

@app.route("/delete_modify", methods=["POST"])
def delete_modify():
    return redirect(url_for("travles_modify_delete"))

@app.route("/travles_modify_delete", methods=["POST", "GET"])
def travles_modify_delete():
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM travels_info ORDER BY id DESC")
        data = cur.fetchall()
    return render_template("travles_delete.html", data=data)

@app.route("/delete/<int:travel_id>")
def delete(travel_id):
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM travels_info WHERE id=?", (travel_id,))
        con.commit()
    return redirect(url_for("travles_modify_delete"))

@app.route("/modify/<int:travel_id>")
def modify(travel_id):
    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM travels_info WHERE id=?", (travel_id,))
        data = cur.fetchall()
    return render_template("travels_modify_page.html", data=data)

@app.route("/update_travel_details", methods=["POST"])
def update_travel_details():
    if request.method == "POST":
        try:
            ta = request.form["Travels_name"]
            vn = request.form["Vehicle_Number"]
            avs = request.form["Available_Seats"]
            form = request.form["From"]
            to = request.form["To"]
            am = request.form["Amount"]
            travel_id = request.args.get("id")

            Front_Image = request.files["Front_Image"]
            Inside_Image = request.files["Inside_Image"]

            front_image_filename = secure_filename(Front_Image.filename)
            inside_image_filename = secure_filename(Inside_Image.filename)
            Front_Image.save(os.path.join(app.config["UPLOAD_FOLDER"], front_image_filename))
            Inside_Image.save(os.path.join(app.config["UPLOAD_FOLDER"], inside_image_filename))

            with sqlite3.connect("passenger.db") as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE travels_info
                    SET "Travels Name" = ?, 
                        "Vehicle Number" = ?, 
                        "Front Image" = ?, 
                        "Inside Image" = ?, 
                        "Available_Scats" = ?, 
                        "From_Location" = ?, 
                        "To_Location" = ?, 
                        "Amount" = ?
                    WHERE id = ?
                """, (ta, vn, front_image_filename, inside_image_filename, avs, form, to, am, travel_id))
                con.commit()
            flash("Travel details updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating travel details: {e}", "error")
        finally:
            return redirect(url_for("delete_modify"))

@app.route("/user_info")
def user_info():
    session.pop("session_name", None)
    return render_template("user_full_information.html")

@app.route("/user_full_info", methods=["POST"])
def user_full_info():
    if request.method == "POST":
        name = request.form.get("name")
        mobile_no = request.form.get("number")
        email = request.form.get("email")

        if name and mobile_no and email:
            try:
                with sqlite3.connect("passenger.db") as con:
                    cur = con.cursor()
                    cur.execute("""
                        INSERT INTO user_information (name, mobile_no, email)
                        VALUES (?, ?, ?)
                    """, (name, mobile_no, email))
                    con.commit()
                return redirect(url_for("tickit_pay"))
            except Exception as e:
                flash(f"An error occurred: {e}", "error")
                return redirect(url_for("user_info"))
        else:
            flash("All fields are required", "error")
            return redirect(url_for("user_info"))

@app.route("/both_data_use", methods=["GET", "POST"])
def both_data_use():
    if request.method == "POST":
        return redirect(url_for("both_data_use"))

    with sqlite3.connect("passenger.db") as con:
        cur = con.cursor()
        query = """
            SELECT 
                pd.id, 
                pd.From_Location, 
                pd.To_Location, 
                pd.Departure, 
                pd.Arrival, 
                ui.name, 
                ui.mobile_no, 
                ui.email 
            FROM passenger_data pd
            JOIN user_information ui ON pd.id = ui.id
        """
        cur.execute(query)
        combined_data = cur.fetchall()

    return render_template("all_user_info_main.html", combined_data=combined_data)

@app.route("/all_data_use", methods=["GET", "POST"])
def all_data_use():
    return redirect(url_for("both_data_use"))

@app.route("/tickit_pay")
def tickit_pay():
    return render_template("tickit_pay_ment.html")

@app.route("/tickit_pay_submit", methods=["GET", "POST"])
def tickit_pay_submit():
    return redirect(url_for("scann"))

@app.route("/scann")
def scann():
    return render_template("scanner_of_pay.html")

if __name__ == "__main__":
    app.run(debug=True, port=8584)