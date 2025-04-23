#Imports
from flask import Flask, render_template, redirect, request, url_for
from flask_scss import Scss
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, text,select, insert, update
from Models import db, customer, rep, admins, orderLine, orders

#Creating a flask instance
app = Flask(__name__)
Scss(app)

#Initalize an instance of a database named "database"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

@app.route("/repView", methods=["POST", "GET"])
@login_required
def repPage():
#Function to add a task
    if request.method == "POST":

        # RN ALL FIELDS MUST BE FILLED OUT TO WORK
        newRepTask = rep(repNum = request.form["repNum"],
                      lastName = request.form["l_Name"],
                      firstName = request.form["f_Name"],
                      street = request.form["street"],
                      city = request.form["city"],
                      state = request.form["state"],
                      postalCode = request.form["postalCode"],
                      commission = request.form["commission"],
                      rate = request.form["rate"])

        #Attempt to connect to the database
        try:
            #connect to the database instance.
            db.session.add(newRepTask)
            #commit changes to the database,
            db.session.commit()
            #Once the changes are made to the database, redirect the user to the updated homepage.
            return redirect("/repView")
        except Exception as e:
            #Print out an error
            print(f"ERROR:{e}")
            #Return an error as well, beause this function must return something.
            return f"ERROR:{e}"
    #Function to see all current tasks (it is an else becuase we always want the website to render with all database tasks shown.)
    else:
        tasks = rep.query.order_by(rep.repNum).all()
        #Render the website  IMPORTANT!!! in "tasks = tasks" the left tasks refers to "tasks" in idex.html, right tasks refers to "tasks" as defined above.
        return render_template("rep.html", tasks = tasks)
    
@app.route("/customerUpdate", methods=["GET", "POST"])
@login_required
def updateCreditLimit(name, newCreditLimit):
    cust = customer.query.get(name)
    cust.creditLimit = newCreditLimit
    db.session.commit()

@app.route("/customerReport", methods=["GET", "POST"])
@login_required
def customerReport():
    customerInfo = None  # Default: don't show anything
    if request.method == "POST":
        name = request.form.get("custName", "").strip()

        if not name:
            customerInfo = {"ENTER CUSTOMER NAME", "0"}
        else:
            stmt = select(
                        customer.customerName, 
                        func.coalesce(func.sum(orderLine.quotedPrice), 0))\
                            .where(func.lower(customer.customerName) == name.lower())\
                            .outerjoin(orders, orders.customerNum == customer.customerNum)\
                            .outerjoin(orderLine, orderLine.orderNum == orders.orderNum)\
                            .group_by(customer.customerName)

            result = db.session.execute(stmt).one_or_none()

            if result is None:
                customerInfo = f"No data found for '{name}'.", "0"
            else:
                customerInfo = result

    return render_template("customerReport.html", customerInfo=customerInfo)

@app.route("/report/")
@login_required
def generateReport():
    repInfo = select(rep.lastName, rep.firstName,\
        func.count(customer.customerNum),\
        func.coalesce(func.round(func.sum(customer.balance) / func.count(customer.customerNum), 2), 0))\
            .group_by(rep.lastName, rep.firstName)\
            .outerjoin(customer, customer.repNum == rep.repNum)
    
    info = db.session.execute(repInfo)
  
    return render_template("report.html", result = info)

@app.route("/deleteRep/<repNum>")
@login_required
def deleteRep(repNum):
    #Get the task that needs to be deleted based on the id provided.
    
    try:
        rep.query.filter(rep.repNum == repNum).delete()
        #connect to the session and delete the task by id
        #commit changes to the database
        db.session.commit()
        #Once changes are made, update the homepage of the website
        return redirect("/repView")
    except Exception as e:
        #Print out an error
        print(f"ERROR:{e}")
        #Return an error as well, beause this function must return something.
        return f"ERROR:{e}"

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = admins.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html", error = None)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return admins.query.get(int(user_id))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if admins.query.filter_by(username=username).first():
            return render_template("sign_up.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = admins(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    return render_template("sign_up.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/")

#start the app itself running
if __name__ == "__main__" :
    #Begins the database instance
    with app.app_context():
        db.create_all()
        
        sql_file = open('inserts.sql','r')
        # Create an empty command string
        sql_command = ''
        # Iterate over all lines in the sql file
        for line in sql_file:
            # Ignore commented lines
            if not line.startswith('--') and line.strip('\n'):
                # Append line to the command string
                sql_command += (" " + line.strip('\n'))

                # If the command string ends with ';', it is a full statement
                if sql_command.endswith(';'):
                    # Try to execute statement and commit it
                    try:
                        db.session.execute(text(sql_command))
                        db.session.commit()
                        print("Inserted object")

                    # Assert in case of error
                    except:
                        pass

                    # Finally, clear command string
                    finally:
                        sql_command = ''
        
        # makes sure there is always at least the default account present on startup
        try:
            defaultUsername = "Admin"
            defaultPasword = "supersecret"
            defaultUser = admins.query.filter_by(username=defaultUsername).first()

            hashedPassword = generate_password_hash(defaultPasword, method="pbkdf2:sha256")

            if not defaultUser:
                addAdmin = insert(admins).values(username=defaultUsername, password=hashedPassword)
                db.session.execute(addAdmin)
                db.session.commit()
                print("Inserted default")

            elif defaultUser and not (defaultUser.password == check_password_hash(defaultPasword)):
                updateAdmin = update(admins)\
                .where(admins.username == "Admin")\
                .values(password = generate_password_hash(defaultPasword, method="pbkdf2:sha256"))
                db.session.execute(updateAdmin)
                db.session.commit()
        except:
            print("error")
    #Actually begins the program
    app.run(debug=True)