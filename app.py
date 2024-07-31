import datetime
from flask import Flask, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


#setting up flask
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

#setting up database
con = sqlite3.connect("project.db", check_same_thread=False)
db = con.cursor()

#setting up session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "serenity"


#setting up routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods = ["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            print("all fields are required")
            return redirect("/register")
        elif password != confirmation:
            print("confirmation don't match your password")
            return redirect("/register")
        elif list(db.execute("SELECT * FROM users WHERE username = ?", (username,))) != []:
            print("username already taken")
            return redirect("/register")
        
        hash = generate_password_hash(password)

        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash))
        con.commit()

        row = db.execute("SELECT id FROM users WHERE username = ?", (username,))
        session["user_id"] = row.fetchone()[0]

        return redirect("/")
        
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            print("provide username and password")
            return redirect("/login")
        
        rows = db.execute("SELECT id, username, hash FROM users WHERE username = ?", (username,))
        data = rows.fetchone()

        if data == None or not check_password_hash(data[2], password):
            print("invalid username and/or password")
            return redirect("/login")

        session["user_id"] = data[0]

        ###TODOset rated active job to no if time has passed by

        user_id = session["user_id"]
        data2 = db.execute("SELECT ratings.job_id, ratings.timestamp FROM ratings INNER JOIN jobs ON ratings.job_id = jobs.id WHERE ratings.user_id = ? AND jobs.end = '' AND jobs.rated = 'Yes';", (user_id,))
        ratings = data2.fetchall()
        today_month = datetime.date.today().month
        today_year = datetime.date.today().year
        
        for rating in ratings:
            lst = rating[1].split("-")
            if int(lst[0]) < today_year or int(lst[1]) < today_month:
                db.execute("UPDATE jobs SET rated = 'No' WHERE id = ?;", (rating[0],))
                con.commit()

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/rate", methods=["GET", "POST"])
def rate():


    try:
        user_id = session["user_id"]
    except(KeyError):
        return redirect("/login")

    if request.method == "POST":

        #variables
        job_id = request.form.get("job")
        overtime = request.form.get("overtime")
        paid = request.form.get("paid")
        tip = request.form.get("tip")
        fair = request.form.get("fair")
        atmosphere = request.form.get("atmosphere")
        team = request.form.get("team")
        communication = request.form.get("communication")
        management = request.form.get("management")
        guests = request.form.get("guests")
        overall = request.form.get("overall")
       

        #check if user cooperates(beta)
        if not job_id or not overtime or not paid or not tip or not fair or not atmosphere or not team or not communication or not management or not guests or not overall:
            print("all fields are required")
            return redirect("/rate")
        
        #check if job already has rating
        data1 = db.execute("SELECT rated FROM jobs WHERE id = ?", (job_id,))
        rated = data1.fetchone()[0]
        if rated == "Yes":
            print("Job already rated")
            return redirect("/rate")

        #add rating to data (todo: limit number of ratings for same job)
        timestamp = datetime.datetime.now()
        db.execute("INSERT INTO ratings (user_id, job_id, timestamp, overtime, overtime_paid, tip, tip_dist, atmosphere, team, communication, management, guests, overall) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, job_id, timestamp, overtime, paid, tip, fair, atmosphere, team, communication, management, guests, overall))
        con.commit()

        #update jobs rated
        db.execute("UPDATE jobs SET rated = 'Yes' WHERE id = ?", (job_id,))
        con.commit()
        
        return redirect("/")
    
    else:
        rows = db.execute("SELECT employer.name, jobs.start, jobs.id FROM jobs INNER JOIN employer ON employer.id = jobs.employer_id WHERE jobs.user_id = ? AND jobs.rated = 'No'", (user_id,))
        jobs = rows.fetchall()

        return render_template("rate.html", jobs=jobs)


@app.route("/browse", methods=["GET", "POST"])
def browse():

    rows1 = db.execute("SELECT name FROM employer;")
    employer = rows1.fetchall()

    if request.method == "GET":
        return render_template("browse.html", render_option = 1, employer = employer)
    
    else:
        search_input = request.form.get("browse")

        rows2 = db.execute("SELECT * FROM employer WHERE name = ?",(search_input,)).fetchall()
        employer_id = rows2[0][0]
        address = rows2[0][3]
        city = rows2[0][2]
        homepage = rows2[0][6]
        number = rows2[0][8]

        rows3 = db.execute("SELECT * FROM jobs INNER JOIN ratings ON jobs.id = ratings.job_id WHERE jobs.employer_id = ?", (employer_id,)) 
        data = rows3.fetchall()

        if len(data) == 0:
            return render_template("browse.html", render_option = 2, employer = employer)

        sum_ratings = 0

        sum_atmosphere = 0
        sum_team = 0
        sum_communicaton = 0
        sum_management = 0
        sum_guests = 0
        sum_overall = 0
        sum_salary_service = 0
        sum_salary_kitchen = 0
        sum_overtime_service = 0
        sum_overtime_kitchen = 0
        sum_tip_service = 0
        sum_tip_kitchen = 0
        sum_paid_service = [0,0]
        sum_paid_kitchen = [0,0]
        sum_distribution_service = [0,0]
        sum_distribution_kitchen = [0,0]
        y_n = ["Yes", "No"]
        types = ["Part Time", "Full Time", "Student", "Minijob"]
        amount_types = [0,0,0,0]
        positions = ["Allrounder", "Barkeeper", "Chef", "Waitor"]
        amount_positions = [0,0,0,0]
        responsibility = [0,0]

        for rating in data:
            sum_ratings += 1
            sum_atmosphere += rating[-6]
            sum_team += rating[-5]
            sum_communicaton += rating[-4]
            sum_management += rating[-3]
            sum_guests += rating[-2]
            sum_overall += rating[-1]

            if rating[3] == "Part_time":
                amount_types[0] += 1
            elif rating[3] == "Full_time":
                amount_types[1] += 1
            elif rating[3] == "Student":
                amount_types[2] += 1
            elif rating[3] == "Minijob":
                amount_types[3] += 1

            if rating[6] == "Allrounder":
                amount_positions[0] += 1
            elif rating[6] == "Barkeeper":
                amount_positions[1] += 1
            elif rating[6] == "Chef":
                amount_positions[2] += 1
            elif rating[6] == "Waitor":
                amount_positions[3] += 1

            if rating[4] == y_n[0]:
                responsibility[0] += 1
            elif rating[4] == y_n[1]:
                responsibility[1] += 1

            if rating[5] == "Service":
                sum_salary_service += rating[7]
                sum_overtime_service += rating[-10]
                sum_tip_service += rating[-8]
                if rating[-9] == "Yes":
                    sum_paid_service[0] += 1
                elif rating[-9] == "No":
                    sum_paid_service[1] += 1
                if rating[-7] == "Yes":
                    sum_distribution_service[0] += 1
                elif rating[-7] == "No":
                    sum_distribution_service[1] += 1

            elif rating[5] == "Kitchen":
                sum_salary_kitchen += rating[7]
                sum_overtime_kitchen += rating[-10]
                sum_tip_kitchen += rating[-8]
                if rating[-9] == "Yes":
                    sum_paid_kitchen[0] += 1
                elif rating[-9] == "No":
                    sum_paid_kitchen[1] += 1
                if rating[-7] == "Yes":
                    sum_distribution_kitchen[0] += 1
                elif rating[-7] == "No":
                    sum_distribution_kitchen[1] += 1


        return render_template("browse.html", render_option = 3, employer = employer, name = search_input,
                               address = address, city = city, homepage = homepage, number = number, sum_ratings = sum_ratings, 
                               atmosphere = round(sum_atmosphere/sum_ratings, 1), team = round(sum_team/sum_ratings, 1),
                               communication = round(sum_communicaton/sum_ratings, 1), management = round(sum_management/sum_ratings, 1),
                               guests = round(sum_guests/sum_ratings, 1), overall = round(sum_overall/sum_ratings,1), 
                               salary_kitchen = round(sum_salary_kitchen/sum_ratings, 1), salary_service = round(sum_salary_service/sum_ratings, 1), 
                               overtime_kitchen = round(sum_overtime_kitchen/sum_ratings, 1), overtime_service = round(sum_overtime_service/sum_ratings, 1), 
                               tip_kitchen = round(sum_tip_kitchen/sum_ratings, 1), tip_service = round(sum_tip_service/sum_ratings, 1), 
                               y_n = y_n, sum_paid_service = sum_paid_service, sum_distribution_service = sum_distribution_service, 
                               sum_paid_kitchen = sum_paid_kitchen, sum_distribution_kitchen = sum_distribution_kitchen, 
                               types = types, amount_types = amount_types, positions = positions, amount_positions = amount_positions, responsibility = responsibility)


@app.route("/addemployer", methods=["GET", "POST"])
def add_employer():

    if request.method == "GET":
        return render_template("addemployer.html")
    
    else:
        name = request.form.get("employer_name")
        gastro_type = request.form.get("gastro_type")
        city = request.form.get("city")
        neighbourhood = request.form.get("neighbourhood")
        address = request.form.get("address")
        homepage = request.form.get("homepage")
        mail = request.form.get("mail")
        number = request.form.get("number")

        if not name or not gastro_type or not city or not neighbourhood:
            print("all fields are required")
            return redirect("/addemployer")
        elif list(db.execute("SELECT * FROM employer WHERE name = ? AND city = ? AND neighbourhood = ?", (name, city, neighbourhood))) != []:
            print("Employer does already exist")
            return redirect("/addemployer")
        
        db.execute("INSERT INTO employer (name, type, city, neighbourhood, address, homepage, mail, number) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, gastro_type, city, neighbourhood, address, homepage, mail, number))
        con.commit()

        return redirect("/addjob")

###todo: passsword change, age/year birth, experience on cv
@app.route("/profil", methods=["GET", "POST"])
def profil():
    user_id = session["user_id"]

    if request.method == "GET":
        row = db.execute("SELECT username, experience, gender, year_birth FROM users WHERE id = ?", (user_id,))
        data = row.fetchone()
        username = data[0]
        experience = data[1]
        gender = data[2]
        age = data[3]
        today = datetime.date.today().year
        if age != None:
            age = today - age
        
        row2 = db.execute("SELECT employer.name, jobs.position, jobs.type, jobs.responsibility, jobs.salary, jobs.start, jobs.end FROM jobs INNER JOIN employer ON jobs.employer_id=employer.id WHERE jobs.user_id = ? ORDER BY jobs.start DESC;", (user_id,))
        cv = row2.fetchall()

        return render_template("profil.html", username=username, experience=experience, gender=gender, age=age, cv=cv)

    else:
        year_birth = request.form.get("year_birth")
        gender = request.form.get("gender")

        db.execute("UPDATE users SET year_birth = ?, gender = ? WHERE id = ?", (year_birth, gender, user_id))
        con.commit()

        return redirect("profil")

@app.route("/addjob", methods=["GET", "POST"])
def profil_addjob():
    if request.method == "GET":

        rows = db.execute("SELECT name FROM employer;")
        employer = rows.fetchall()

        return render_template("profil_addjob.html", employer=employer)
    
    else:
        user_id = session["user_id"]
        
        employer_name = request.form.get("employer_name")
        employer = db.execute("SELECT id FROM employer WHERE name = ?", (employer_name,))
        employer_id = employer.fetchone()[0]

        workspace = request.form.get("workspace")
        position = request.form.get("position")
        employ_type = request.form.get("employment_type")
        responsibility = request.form.get("responsibility")
        salary = request.form.get("salary")
        start = request.form.get("start")
        end = request.form.get("end")

        if not employer_name or not workspace or not position or not employ_type or not responsibility or not salary or not start:
            print("Fill in all required fields")
            return redirect("/addjob")
        elif list(db.execute("SELECT * FROM jobs WHERE user_id = ? AND employer_id = ? AND position = ? AND type = ? AND responsibility = ?", (user_id, employer_id, position, employ_type, responsibility))) != []:
            print("Already added that job")
            return redirect("/addjob")
        elif not end and len(list(db.execute("SELECT * FROM jobs WHERE user_id = ? AND end = ''; ", (user_id, )))) >= 2:
            print("Only two active jobs allowed")
            return redirect("/addjob") 
        
        db.execute("INSERT INTO jobs (user_id, employer_id, type, responsibility, workspace, position, salary, start, end) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, employer_id, employ_type, responsibility, workspace, position, salary, start, end))
        con.commit()

        return redirect("/profil")


@app.route("/history")
def profil_history():

    user_id = session["user_id"]
    data = db.execute("SELECT employer.name, ratings.overtime, ratings.tip, ratings.atmosphere, ratings.team, ratings.communication, ratings.management, ratings.guests, ratings.overall, ratings.timestamp FROM ratings INNER JOIN jobs ON ratings.job_id = jobs.id INNER JOIN employer ON jobs.employer_id = employer.id WHERE ratings.user_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id,))
    ratings = data.fetchall()
    return render_template("profil_history.html", ratings=ratings)

@app.route("/stats")
def stats():

    user1 = db.execute("SELECT COUNT(*) FROM users")
    amount_user = user1.fetchone()[0]

    user2 = db.execute("SELECT COUNT(*) FROM users WHERE gender = 'male'")
    amount_male = user2.fetchone()[0]
    user3 = db.execute("SELECT COUNT(*) FROM users WHERE gender = 'female'")
    amount_female = user3.fetchone()[0]
    user4 = db.execute("SELECT COUNT(*) FROM users WHERE gender = 'non-binary'")
    amount_non_binary = user4.fetchone()[0]
    user5 = db.execute("SELECT COUNT(*) FROM users WHERE gender IS NULL")
    amount_null = user5.fetchone()[0]
    gender1 = [amount_male, amount_female, amount_non_binary, amount_null]
    gender2 = ["Male", "Female", "Non-binary", "Unknown"]

    user6 = db.execute("SELECT year_birth FROM users")
    birthdays_fetch = user6.fetchall()
    birthdays = [0,0,0,0,0,0]
    ages = ["60+", "41-60", "31-40", "21-30", "under 21", "unknown"]
    sum_years = 0
    amount_known_birthdays = 0

    for birthday in birthdays_fetch:
        if birthday[0] == None:
            birthdays[5] += 1
        else: 
            if birthday[0] < 1964:
                birthdays[0] += 1
            elif 1964 <= birthday[0] < 1983:
                birthdays[1] += 1
            elif 1983 <= birthday[0] < 1993:
                birthdays[2] += 1
            elif 1993 <= birthday[0] < 2003:
                birthdays[3] += 1
            else: 
                birthdays[4] += 1

            sum_years += birthday[0]
            amount_known_birthdays += 1

    average_year = sum_years/amount_known_birthdays
    average_age = round(datetime.date.today().year - average_year)
    
    return render_template("stats.html", amount_user=amount_user, gender1 = gender1, gender2 = gender2, birthdays=birthdays, ages=ages, average_age=average_age)

@app.route("/employerstats")
def emp_stats():

    employer = db.execute("SELECT COUNT(*) FROM employer")
    amount_employer = employer.fetchone()[0]

    gastro_types_amount = [0,0,0,0,0]
    gastro_types = ["Restaurant", "Bar", "Canteen", "Beer Garden", "Unknown"]
    employer2 = db.execute("SELECT COUNT(*), type FROM employer GROUP BY type")
    all_types = employer2.fetchall()
    for type in all_types:
        if type[1] == None:
            gastro_types_amount[-1] += type[0]
        elif type[1] == "Restaurant":
            gastro_types_amount[0] += type[0]
        elif type[1] == "Bar":
            gastro_types_amount[1] += type[0]
        elif type[1] == "Canteen":
            gastro_types_amount[2] += type[0]
        elif type[1] == "Beer Garden":
            gastro_types_amount[3] += type[0]

    return render_template("stats_employer.html", amount_employer=amount_employer, gastro_types_amount=gastro_types_amount, gastro_types=gastro_types)

@app.route("/jobstats")
def job_stats():

    jobs1 = db.execute("SELECT COUNT(*) FROM jobs")
    registrated_jobs = jobs1.fetchone()[0]

    jobs2 = db.execute("SELECT COUNT(*) FROM jobs WHERE end = ''")
    active_jobs = jobs2.fetchone()[0]

    jobs3 = db.execute("SELECT position, COUNT(*) FROM jobs GROUP BY position;")
    job_positions = jobs3.fetchall()
    positions = []
    amount_position = []
    for i in range(len(job_positions)):
        positions.append(job_positions[i][0])
        amount_position.append(job_positions[i][1])

    jobs4 = db.execute("SELECT type, COUNT(*) FROM jobs GROUP BY type;")
    job_types = jobs4.fetchall()
    emp_types = []
    amount_types = []
    for i in range(len(job_types)):
        emp_types.append(job_types[i][0])
        amount_types.append(job_types[i][1])

    jobs5 = db.execute("SELECT COUNT(*) FROM jobs WHERE responsibility = 'Yes'")
    jobs_with_responsibility = jobs5.fetchone()[0]
    quota_responsibility = round(jobs_with_responsibility/registrated_jobs, 2)

    jobs6 = db.execute("SELECT SUM(salary) FROM jobs WHERE end = '';")
    sum_salary_active = jobs6.fetchone()[0]
    average_salary_active = round(sum_salary_active/active_jobs, 2)

    jobs7 = db.execute("SELECT SUM(ratings.overtime) FROM ratings INNER JOIN jobs ON jobs.id = ratings.job_id WHERE jobs.end = '';")
    sum_overtime_active = jobs7.fetchone()[0]
    average_overtime_active = round(sum_overtime_active/active_jobs, 2)

    jobs8 = db.execute("SELECT SUM(ratings.tip) FROM ratings INNER JOIN jobs ON jobs.id = ratings.job_id WHERE jobs.end = '';")
    sum_tip_active = jobs8.fetchone()[0]
    average_tip_active = round(sum_tip_active/active_jobs, 2)


    return render_template("stats_jobs.html", registrated_jobs=registrated_jobs, 
                           active_jobs=active_jobs, positions=positions, amount_position=amount_position, 
                           emp_types=emp_types, amount_types=amount_types, quota_responsibility = quota_responsibility,
                           average_salary_active = average_salary_active, average_overtime_active = average_overtime_active,
                           average_tip_active = average_tip_active)