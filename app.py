import os
from collections import Counter

from sqlalchemy import create_engine, text
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# special helping function credit: cs50's implemenatation of finance
from helpers import norm, login_required, check_required


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Library to use SQLite database
engine = create_engine("sqlite:///prescriptions.db", future=True)

with engine.begin() as conn:
    # waits up to 5 seconds
    conn.execute(text("PRAGMA busy_timeout = 5000"))
    conn.execute(text("PRAGMA foreign_keys = ON"))

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget user_id, sent and check status
    session.clear()
    session["sent"] = False
    session["checked"] = False

    # if login form submitted
    if request.method == "POST":
        # Get username and password
        username = request.form.get("username")
        password = request.form.get("password")

        # Error checking
        # Ensure username was submitted
        if not username:
            flash("Missing username!", "danger")
            return render_template("login.html")

        # Ensure password was submitted
        elif not password:
            flash("Missing password!", "danger")
            return render_template("login.html")

        # Query to database
        with engine.connect() as conn:
            user = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username}).mappings().first()

        # Check if account exist or if password was right
        if not user or not check_password_hash(user["hash"], password):
            flash("Invalid username and/or password", "danger")
            return render_template("login.html")

        # After all finish login user
        session["user_id"] = user["id"]
        flash("logged in!", "success")
        return redirect("/")

    # if login page was viewed
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # clear user info and thus login status
    session.clear()

    # redirect to index which login_required would direct to login page
    flash("logged out!")
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # if request form submitted
    if request.method == "POST":
        # ---Account Basic info---
        username = request.form.get("username")
        # Check if an username already exists
        with engine.connect() as conn:
            user = conn.execute(text("SELECT id FROM users WHERE username = :name"), {"name": username}).mappings().first()
        if user:
            flash("Username already exists!", "danger")
            return render_template("register.html")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Error checking
        # Ensure username was submitted
        if not username:
            flash("Missing username", "danger")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("Missing password!", "danger")
            return render_template("register.html")

        # Ensure password and confirmation matched
        elif password != confirmation:
            flash("Passwords don't match for both inputs!", "danger")
            return render_template("register.html")


        # ---Account Additinal info---
        doctor_info = {
            "name": request.form.get("doctor-name"),
            "qualification": request.form.get("qualification"),
            "department": request.form.get("department"),
            "registration": request.form.get("registration")
            }

        clinic_info = {
            "name": request.form.get("clinic-name"),
            "address": request.form.get("address"),
            "contact": request.form.get("contact"),
            "email": request.form.get("email")
            }

        # After all above ensured try INSERTing user
        try:
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO users(username, hash) VALUES(:name, :hash)"),
                    {"name": username, "hash": generate_password_hash(password)})
                
                # Get id of new user(get last user, that was autoincrement)
                user_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()

                # INSERT INTO doctors
                conn.execute(text("INSERT INTO doctors(user_id, doctor_name, qualification, department, registration) VALUES(:uid, :dname, :qual, :dep, :reg)"),
                    {"uid": user_id, "dname": doctor_info["name"], "qual": doctor_info["qualification"], "dep": doctor_info["department"], "reg": doctor_info["registration"]})
                # INSERT INTO clinics
                conn.execute(text("INSERT INTO clinics(user_id, clinic_name, address, contact, email) VALUES(:uid, :cname, :addr, :cont, :email)"),
                    {"uid": user_id, "cname": clinic_info["name"], "addr": clinic_info["address"], "cont": clinic_info["contact"], "email": clinic_info["email"]})

        except Exception as e:
            app.logger.error(f"User registration failed: {e}")
            flash("Sorry, registration failed. Please try again/later.", "danger")
            return render_template("register.html")

        # redirect to login page
        flash("Registered successfully!", "success")
        return redirect("/login")

    # if register page viewed
    else:
        return render_template("register.html")

# Route for AJAX query to users for new user registration
@app.route("/users")
def users():
    # Get New user typed username
    name = request.args.get("name")
    # Check if this username belongs to any other user
    with engine.connect() as conn:
        user = conn.execute(text("SELECT id FROM users WHERE username = :name"), {"name": name}).mappings().first()
    if user:
        return jsonify({"msg": "This Username is already taken"})
    else:
        return jsonify({"msg": ""})


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Prescription Page"""

    # Get user_id
    user_id = session["user_id"]

    # If prescription was submit
    if request.method == "POST":
        # ---Data Collection---
        # Get Date
        day = norm(request.form.get("day"))
        month = norm(request.form.get("month"))
        year = norm(request.form.get("year"))

        # Get Patient Info
        patient_name = request.form.get("patient-name")
        # Check if patient name is given or else return
        if not patient_name:
            flash("Missing patient name!", "danger")
            return redirect ("/")

        age = request.form.get("age")
        sex = request.form.get("sex")

        # Get Vitals Info
        chief_complaints = request.form.get("chief-complaints")
        on_examination = request.form.get("on-examination")
        test_advised = request.form.get("test-advised")
        diagnosis = request.form.get("diagnosis")

        # Get med Info(The total List of Info)
        med_names = request.form.getlist("med_name[]")
        doses = request.form.getlist("dose[]")
        forms = request.form.getlist("form[]")
        schedules = request.form.getlist("schedule[]")
        timings = request.form.getlist("timing[]")
        durations = request.form.getlist("duration[]")

        # ---Start Execution(INSERT)---
        prescription_id = None
        try:
            with engine.begin() as conn:
                # Execute Prescription Info into prescriptions
                result = conn.execute(
                    text("INSERT INTO prescriptions(user_id, day, month, year) VALUES(:uid, :day, :month, :year) RETURNING id"),
                    {"uid": user_id, "day": day, "month": month, "year": year}
                )
                prescription_id = result.scalar()

                # Insert into patients
                conn.execute(
                    text("INSERT INTO patients(prescription_id, patient_name, age, sex) VALUES (:prid, :pname, :age, :sex)"),
                    {"prid": prescription_id, "pname": patient_name, "age": age, "sex": sex}
                )

                # Execute Vitals Info into vitals
                conn.execute(
                    text("INSERT INTO vitals(prescription_id, chief_complaints, on_examination, test_advised, diagnosis) VALUES (:prid, :chief, :exam, :test, :diag)"),
                    {"prid": prescription_id, "chief": chief_complaints, "exam": on_examination, "test": test_advised, "diag": diagnosis}
                )

                # Execute each med Info into medications
                for index, (name, dose, form, schedule, timing, duration) in enumerate(zip(med_names, doses, forms, schedules, timings, durations), start=1):
                    if name: # Only if there's a name
                        conn.execute(
                            text("""INSERT INTO medications
                                (prescription_id, sequence, med_name, dose, form, schedule, timing, duration, user_id)
                                VALUES (:prid, :seq, :name, :dose, :form, :schedule, :timing, :duration, :uid)"""),
                            {
                                "prid": prescription_id,
                                "seq": index,
                                "name": name,
                                "dose": dose,
                                "form": form,
                                "schedule": schedule,
                                "timing": timing,
                                "duration": duration,
                                "uid": user_id
                            }
                        )

                # Finish Execution
                flash("Prescription saved successfully.", "success")
                return redirect(url_for("view", id=prescription_id))

        except Exception as e:
            err_text = str(e)
            if "UNIQUE constraint failed" in err_text:
                flash("This prescription ID is already being used.")
            elif "database is locked" in err_text:
                flash("Another user is editing this prescription. Please try again.")
            else:
                flash("An unexpected error occurred while saving.")

            print(f"[DB ERROR] prescription insert failed: {err_text}")
            return render_template("index.html")
        
    else:
        with engine.connect() as conn:
            # Greet User(If haven't already) and provide instruction
            username_row = conn.execute(text("SELECT username FROM users WHERE id = :id"), {"id": user_id}).mappings().first()
            username = username_row["username"]

            if not session.get("greet"):
                flash(f"Welcome {username}, Fill out the patient and prescription fields to create a new prescription.", "primary")
                session["greet"] = True

            # Send All data only if it was not sent...
            if not session.get("sent"):
                # Prepare to send (note: as output is row mapping obj you have to convert them into dict before sending JSON)
                # Get Doctor Info
                doctor_row = conn.execute(text("SELECT * FROM doctors WHERE user_id = :id"), {"id": user_id}).mappings().first()
                # Get Clinic Info
                clinic_row = conn.execute(text("SELECT * FROM clinics WHERE user_id = :id"), {"id": user_id}).mappings().first()

                # Get medData in {med_name: {type: [Data,...],...},...} structure
                med_data = {}
                med_rows = conn.execute(text("SELECT * FROM medications WHERE user_id = :id"), {"id": user_id}).mappings().all()

                types = ["dose", "form", "schedule", "timing", "duration"]

                for row in med_rows:
                    med_name = row["med_name"]
                    # Initialize med_data[med_name] as struct: med_data = {med_name: {_}}
                    med_data.setdefault(med_name, {})
                    for type in types:
                        # Initialize med_data[med_name][type] as struct: med_data = {med_name: {type_data: [_]}}
                        # Store raw values (list)
                        med_data[med_name].setdefault(f"{type}_data", []).append(row[type])

                # Convert each list into unique, frequency-sorted lists
                for med_name, med_dict in med_data.items():
                    for type in types:
                        values = med_dict[f"{type}_data"]
                        counts = Counter(values)
                        # Replace with frequency-sorted unique list
                        med_dict[f"{type}_data"] = [val for val, _ in counts.most_common()]

                # Mark data as sent
                session["sent"] = True

                # Pass rows directly to template + convert to dict for safe JSON usage
                return render_template(
                    "index.html",
                    doctor_row=dict(doctor_row) if doctor_row else {},
                    clinic_row=dict(clinic_row) if clinic_row else {},
                    med_data=med_data if med_data else {}
                )
            
            # If only account was changed thus, send only account Info
            elif not session.get("account"):
                # Prepare to send (note: as output is row mapping obj you have to convert them into dict before sending JSON)
                # Get Doctor Info
                doctor_row = conn.execute(text("SELECT * FROM doctors WHERE user_id = :id"), {"id": user_id}).mappings().first()
                # Get Clinic Info
                clinic_row = conn.execute(text("SELECT * FROM clinics WHERE user_id = :id"), {"id": user_id}).mappings().first()

                # Mark account data as sent
                session["account"] = True
                # Pass rows directly to template + convert to dict for safe JSON usage
                return render_template(
                    "index.html",
                    doctor_row=dict(doctor_row) if doctor_row else {},
                    clinic_row=dict(clinic_row) if clinic_row else {},
                )
            # Else if all data was sent render only index.html
            else:
                return render_template("index.html")



@app.route("/refresh")
@login_required
def refresh():
    """Refresh prescription med_data"""

    # Send med_data again, loading to index page
    session["sent"] = False
    return redirect("/")



@app.route("/view")
@login_required
def view():
    """View page for prescription"""

    # Get user_id
    user_id = session["user_id"]

    # Provide instruction
    flash("Review of patient’s prescription details and diagnosis below.", "primary")

    # Get prescription_id
    try:
        prescription_id = int(request.args.get("id"))

    except (TypeError, ValueError):
        flash("Invalid prescription ID!", "danger")
        return redirect("/")


    with engine.connect() as conn:
        # Prepare Info
        # Get Prescription Info (+Check if user own this prescription)
        prescription_row = conn.execute(text("SELECT * FROM prescriptions WHERE id = :id AND user_id = :uid"), {"id": prescription_id, "uid": user_id}).mappings().first()

        if not prescription_row: # Send warning
            flash("Sorry, you can't access this Id or it doesn't exists!", "danger")
            return redirect("/")

        # Get Patient Info
        patient_row = conn.execute(text("SELECT * FROM patients WHERE prescription_id = :prid"), {"prid": prescription_id}).mappings().first()

        # Get Vital Info
        vital_row = conn.execute(text("SELECT * FROM vitals WHERE prescription_id = :prid"), {"prid": prescription_id}).mappings().first()

        # Get medications Info (all row)
        medication_rows = conn.execute(text("SELECT * FROM medications WHERE prescription_id = :prid ORDER BY sequence ASC"), {"prid": prescription_id}).mappings().all()

    # Pass rows directly to template + convert to dict for safe JSON usage
    return render_template(
        "view.html",
        prescription=dict(prescription_row),   
        patient=dict(patient_row) if patient_row else {},
        vital=dict(vital_row) if vital_row else {},
        medications=[dict(row) for row in medication_rows] if medication_rows else []
    )


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit prescription"""

    # A hybrid of index and view route
    # Get user_id
    user_id = session["user_id"]

    # Get prescription_id
    try:
        prescription_id = int(request.args.get("id"))
    except (TypeError, ValueError):
        flash("Invalid prescription ID!", "danger")
        return redirect("/")

    with engine.connect() as conn:
        # Get Prescription Info (+Check if user own this prescription)
        prescription_row = conn.execute(text("SELECT * FROM prescriptions WHERE id = :id AND user_id = :uid"), {"id": prescription_id, "uid": user_id}).mappings().first()

        if not prescription_row: # Send warning
            flash("Sorry, you can't access this Id or it doesn't exists!", "danger")
            return redirect("/")


    # If Edit page was submit (Like Index route)
    if request.method == "POST":
        # ---Data Collection---
        # Get Date
        day = norm(request.form.get("day"))
        month = norm(request.form.get("month"))
        year = norm(request.form.get("year"))

        # Get Patient Info
        patient_name = request.form.get("patient-name")
        age = request.form.get("age")
        sex = request.form.get("sex")

        # Get Vitals Info
        chief_complaints = request.form.get("chief-complaints")
        on_examination = request.form.get("on-examination")
        test_advised = request.form.get("test-advised")
        diagnosis = request.form.get("diagnosis")

        # Get med Info
        med_names = request.form.getlist("med_name[]")
        doses = request.form.getlist("dose[]")
        forms = request.form.getlist("form[]")
        schedules = request.form.getlist("schedule[]")
        timings = request.form.getlist("timing[]")
        durations = request.form.getlist("duration[]")

        # ---Start Execution(UPDATE)---
        with engine.begin() as conn:
            # Execute Prescription Info into prescriptions
            conn.execute(text("UPDATE prescriptions SET day = :day, month = :month, year = :year WHERE id = :id"),
                {"day": day, "month": month, "year": year, "id": prescription_id}
            )

            # Execute Patient Info into patients
            conn.execute(text("UPDATE patients SET patient_name = :pname, age = :age, sex = :sex WHERE prescription_id = :prid"),
                {"pname": patient_name, "age": age, "sex": sex, "prid": prescription_id}
            )
                
            # Execute Vitals Info into vitals
            conn.execute(text("UPDATE vitals SET chief_complaints = :chief, on_examination = :exam, test_advised = :test, diagnosis = :diag WHERE prescription_id = :prid"),
                {"chief": chief_complaints, "exam": on_examination, "test": test_advised, "diag": diagnosis, "prid": prescription_id}
            )

            # First Get old prescription medication row-sequence list
            sequences = conn.execute(text("SELECT sequence FROM medications WHERE prescription_id = :prid"), {"prid": prescription_id}).mappings().all()
            sequence_list = [row["sequence"] for row in sequences]  # set of existing sequences

            # Execute each med Info into medications
            for index, (name, dose, form, schedule, timing, duration) in enumerate(zip(med_names, doses, forms, schedules, timings, durations), start=1):
                if name: # Only if there's a name
                    if index in sequence_list: # UPDATE (no need for sequence)
                        conn.execute(
                            text("UPDATE medications SET med_name = :name, dose = :dose, form = :form, schedule = :schedule, timing = :timing, duration = :duration WHERE prescription_id = :prid AND sequence = :seq"),
                            {
                                "name": name, 
                                "dose": dose, 
                                "form": form, 
                                "schedule": schedule, 
                                "timing": timing, 
                                "duration": duration, 
                                "prid": prescription_id, 
                                "seq": index
                            }
                        )

                    else: # INSERT (everything needed)
                        conn.execute(
                            text("""INSERT INTO medications
                                (prescription_id, sequence, med_name, dose, form, schedule, timing, duration, user_id)
                                VALUES (:prid, :seq, :name, :dose, :form, :schedule, :timing, :duration, :uid)"""),
                            {
                                "prid": prescription_id,
                                "seq": index,
                                "name": name,
                                "dose": dose,
                                "form": form,
                                "schedule": schedule,
                                "timing": timing,
                                "duration": duration,
                                "uid": user_id
                            }
                        )

            #---Finish---
        # Display message
        flash("Prescription updated successfully!", "success")
        return redirect(url_for("view", id=prescription_id))


    else: # Like View route
        with engine.connect() as conn:
            # Prepare Info
            # Prescription Info: from top
            
            # Get Patient Info
            patient_row = conn.execute(
                text("SELECT * FROM patients WHERE prescription_id = :prid"), {"prid": prescription_id}).mappings().first()
            
            # Get Vital Info
            vital_row = conn.execute(text("SELECT * FROM vitals WHERE prescription_id = :prid"), {"prid": prescription_id}).mappings().first()

            # Get medications Info (all row)
            medication_rows = conn.execute(text("SELECT * FROM medications WHERE prescription_id = :prid ORDER BY sequence ASC"), {"prid": prescription_id}).mappings().all()

        # Pass rows directly to template + convert to dict for safe JSON usage
        return render_template(
            "edit.html",
            prescription=dict(prescription_row),   
            patient=dict(patient_row) if patient_row else {},
            vital=dict(vital_row) if vital_row else {},
            medications=[dict(row) for row in medication_rows] if medication_rows else []
        )


# Account and associated routes
@app.route("/account")
@login_required
def account():
    """Account Page"""

    # Set check status
    session["checked"] = False

    # Get User Info
    user_id = session["user_id"]
    with engine.connect() as conn:
        user_row = conn.execute(text("SELECT id, username FROM users where id = :id"), {"id": user_id}).mappings().first()

    return render_template("account.html", user=dict(user_row) if user_row else {})

# Route for password check
@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    """Check user"""

    # If check form submit
    if request.method == "POST":
        # Get password
        password = request.form.get("password")

        # Get current user's username, password hash from db plus recheck if user exist
        with engine.connect() as conn:
            user = conn.execute(text("SELECT hash FROM users WHERE id = :id"), {"id": session["user_id"]}).mappings().first()
        
        if user and check_password_hash(user["hash"], password):
            session["checked"] = True
            next_url = session.pop("next_url", url_for("index"))
            return redirect(next_url)
        else:
            flash("Invalid password, please try again.", "danger")

    # Return if visited or failed
    return render_template("check.html")

# Route for changing password
@app.route("/password", methods=["GET", "POST"])
@login_required
@check_required
def password():
    """Change Password"""

    # if password form submitted
    if request.method == "POST":
        # Get user Info
        user_id = session["user_id"]
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Error checking
        # Ensure password was submitted
        if not password:
            flash("Missing password!", "danger")
            return render_template("password.html")

        # Ensure password and confirmation matched
        elif password != confirmation:
            flash("Passwords don't match for both inputs!", "danger")
            return render_template("password.html")

        # After all above ensured try UPDATEing user
        try:
            with engine.begin() as conn:
                conn.execute(text("UPDATE users SET hash = :hash WHERE id = :id"), {"hash": generate_password_hash(password), "id": user_id})

            # redirect to logout
            flash("Password Changed Successfully!", "success")
            return redirect("/logout")
        
        except Exception as e:
            app.logger.error(f"Password Change failed: {e}")
            flash("Password change failed, Please try again/later", "danger")
            return redirect("/account")

    # Return if viewed
    else:
        return render_template("password.html")

# Route for changing account information
@app.route("/change", methods=["GET", "POST"])
@login_required
@check_required
def change():
    """Change user Info"""

    # Get user_id
    user_id = session["user_id"]

    # if form was submit
    if request.method == "POST":

        # Get Account Additinal info
        doctor_info = {
            "name": request.form.get("doctor-name"),
            "qualification": request.form.get("qualification"),
            "department": request.form.get("department"),
            "registration": request.form.get("registration")
            }

        clinic_info = {
            "name": request.form.get("clinic-name"),
            "address": request.form.get("address"),
            "contact": request.form.get("contact"),
            "email": request.form.get("email")
            }

        try:
            with engine.begin() as conn:
                # UPDATE doctors
                conn.execute(text("UPDATE doctors SET doctor_name = :dname, qualification = :qual, department = :dep, registration = :reg WHERE user_id = :uid"),
                    {"dname": doctor_info["name"], "qual": doctor_info["qualification"], "dep": doctor_info["department"], "reg": doctor_info["registration"], "uid": user_id})
                # UPDATE clinics
                conn.execute(text("UPDATE clinics SET clinic_name = :cname, address = :addr, contact = :cont, email = :email WHERE user_id = :uid"),
                    {"cname": clinic_info["name"], "addr": clinic_info["address"], "cont": clinic_info["contact"], "email": clinic_info["email"], "uid": user_id})

            session["account"] = False # To resend account data
            flash("User Information Changed!", "success")
        
        except Exception as e:
            app.logger.error(f"Account Information Change failed: {e}")
            flash("Account Information change failed, Please try again/later", "danger")
    
        # Redirect to account page
        return redirect("/account")

    # if change page viewed
    else:
        return render_template("change.html")



@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search prescriptons"""

    # If search form submit
    if request.method == "POST":
        # Get all data prepared for view
        # Get user_id
        user_id = session["user_id"]

        # Get Prescription Info
        # First check if Id was accessible
        prescription_id = request.form.get("id")
        if prescription_id:
            # First check ID belongs to user
            with engine.connect() as conn:
                check_row = conn.execute(text("SELECT * FROM prescriptions WHERE id = :id AND user_id = :uid"), {"id": prescription_id, "uid": user_id}).mappings().first()
            # If check_id exists
            if check_row:
                return redirect(url_for("view", id=prescription_id))
            else:
                flash("Sorry, you can't access this Id or it doesn't exists!", "danger")
                return render_template("search.html")

        # Else
        # ---Search Begins---
        # Collect filters to get all parameters plus normalize age and dose
        filters = {
            "day": request.form.get("day", "").strip() or None,
            "month": request.form.get("month", "").strip() or None,
            "year": request.form.get("year", "").strip() or None,
            "patient_name": request.form.get("patient-name", "").strip() or None,
            "age": norm(request.form.get("age", "")).strip() or None,
            "sex": request.form.get("sex", "").strip() or None,
            "med_name": request.form.get("med_name", "").strip() or None,
            "form": request.form.get("form", "").strip() or None,
            "dose": norm(request.form.get("dose", "")).strip() or None,
        }

        # Build query (LEFT as not every prescription would have medications)
        query = """
            SELECT prescriptions.id, patient_name, day, month, year, timestamp FROM prescriptions
            JOIN patients ON prescriptions.id = patients.prescription_id
            LEFT JOIN medications ON prescriptions.id = medications.prescription_id
            WHERE prescriptions.user_id = :user_id
        """

        # Get parameters
        params = {}
        params["user_id"] = user_id

        for key in filters:
            if filters[key]:
                if key in ["patient_name", "age", "med_name", "form", "dose"]:
                    query += f" AND LOWER({key}) LIKE LOWER(:{key})"
                    params[key] = f"%{filters[key]}%"
                else:
                    query += f" AND {key} = :{key}"
                    params[key] = filters[key]

        # Final add to query
        query += " GROUP BY prescriptions.id ORDER BY prescriptions.timestamp DESC"

        # Search 
        with engine.connect() as conn:
            data_rows = conn.execute(text(query), params).mappings().all() # with all parameter dict

        # Display Results
        flash("Results!", "success")
        return render_template("results.html", data=[dict(row) for row in data_rows] if data_rows else [])

    # If search page viewed
    else:
        return render_template("search.html")

# Route for AJAX query associated with Search page for Dynamic suggestion
@app.route("/query", methods=["GET"])
@login_required
def query():
    """Query for Search page"""

    # First Get data to make a SQL query
    # Query would pass only the base element value(e.g. value of patient_name, ...)
    base_value = request.args.get("value")
    # Type or ID of element e.g. patient_name, age...
    type = request.args.get("type")
    print(type)

    # mapping for table template and base template
    table_map = {
        "patient_name": ("patients", "patient_name"),
        "age": ("patients", "patient_name"),
        "sex": ("patients", "patient_name"),
        "med_name": ("medications", "med_name"),
        "dose": ("medications", "med_name"),
        "form": ("medications", "med_name"),
    }
    table_tmp, base_tmp = table_map.get(type, (None, None))
    if not table_tmp: # Protecting from Injection attack on {type}
        return jsonify([])

    # Get results
    # Only if base_value present
    if base_value:
        # Case: queryName e.g. patient_name, med_name
        if "name" in type:
            # Seek all Name(e.g. patient_name) suggestion from table // WHERE {base_tmp}column LIKE base_value
            with engine.connect() as conn:
                results = conn.execute(text(f"SELECT {type} FROM {table_tmp} WHERE LOWER({base_tmp}) LIKE LOWER(:base_value) GROUP BY {type} ORDER BY COUNT(*) DESC LIMIT 10"), {"base_value": f"%{base_value}%"}).mappings().all()
        # Case: queryType, queryDropDown e.g. age..., dose...
        else:
            # Seek all type(e.g. age...) suggestion from table based on base(e.g. patient_name) // WHERE {base_tmp}column = base_value
            with engine.connect() as conn:
                results = conn.execute(text(f"SELECT {type} FROM {table_tmp} WHERE LOWER({base_tmp}) = LOWER(:base_value) GROUP BY {type} ORDER BY COUNT(*) DESC LIMIT 10"), {"base_value": base_value}).mappings().all()

        # Alternative: Merge these both(i.e. LIKE = ?) which would allow similar base to get same suggestions of type

    results_list = [dict(row) for row in results]
    return jsonify(results_list)



@app.route("/history")
@login_required
def history():
    """Show all previous prescriptions"""

    # Get user_id
    user_id = session["user_id"]
    # Get all data of user_id prepared for view
    # Data struct[prescription_id, patient_name, date, timestamp]
    with engine.connect() as conn:
        data_rows = conn.execute(text("SELECT id, patient_name, day, month, year, timestamp FROM prescriptions LEFT JOIN patients ON prescriptions.id = patients.prescription_id WHERE user_id = :uid ORDER BY timestamp DESC"), {"uid": user_id}).mappings().all()

    return render_template("history.html", data=[dict(row) for row in data_rows] if data_rows else [])


@app.route("/about")
@login_required
def about():
    """About page"""

    # Get username
    with engine.connect() as conn:
        user_row = conn.execute(text("SELECT username FROM users WHERE id = :uid"), {"uid": session["user_id"]}).mappings().first()
    # Display and Greet!
    flash(f"Welcome {user_row["username"]}!", "success")
    return render_template("about.html", username=user_row["username"])

