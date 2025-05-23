# Imports
from flask import Flask, render_template, redirect, request, url_for
from flask_scss import Scss
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, text, select, insert, update, exc
from Models import db, customer, rep, admins, orderLine, orders

# Creating a flask instance
app = Flask(__name__)
Scss(app)

# Initalize an instance of a database named "database" and configure
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

db.init_app(app)

# set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"

# Allows the addition/removal of representatives
@app.route("/repView", methods=["POST", "GET"])
@login_required
def repPage():
    error_message = None
    # Function to add a task
    if request.method == "POST":
        try:
            # Validate and convert numeric fields
            rep_num = int(request.form["repNum"])
            commission = float(request.form["commission"])
            rate = float(request.form["rate"])

            newRepTask = rep(repNum=rep_num,
                             lastName=request.form["l_Name"],
                             firstName=request.form["f_Name"],
                             street=request.form["street"],
                             city=request.form["city"],
                             state=request.form["state"],
                             postalCode=request.form["postalCode"],
                             commission=commission,
                             rate=rate)

            # Attempt to connect to the database
            db.session.add(newRepTask)
            # commit changes to the database,
            db.session.commit()
            # Once the changes are made to the database, redirect the user to the updated homepage.
            return redirect("/repView")
        except ValueError:
            error_message = "Invalid input for Rep Number, Commission, or Rate. Please enter valid numbers."
        except exc.IntegrityError:
             db.session.rollback() # Rollback the session in case of integrity error (e.g., duplicate repNum)
             error_message = f"Representative Number '{request.form['repNum']}' already exists."
        except Exception as e:
            db.session.rollback() # Rollback on other potential errors
            # Print out an error
            print(f"ERROR:{e}")
            # Return an error as well, beause this function must return something.
            error_message = f"An unexpected error occurred: {e}"

    # Fetch tasks regardless of method (GET or POST with error)
    tasks = rep.query.order_by(rep.repNum).all()
    # Render the template, passing tasks and any error message
    return render_template("rep.html", tasks=tasks, error=error_message)

# Generates report for customers based on name
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

# Generates report for all representatives
@app.route("/report")
@login_required
def generateReport():
    repInfo = select(rep.lastName,
                     rep.firstName,
                     func.count(customer.customerNum).label("num_customers"),
                     func.coalesce(func.round(func.sum(customer.balance) / func.count(customer.customerNum), 2), 0))\
        .group_by(rep.lastName, rep.firstName)\
        .outerjoin(customer, customer.repNum == rep.repNum)

    info = db.session.execute(repInfo)

    return render_template("report.html", result=info)

@app.route("/deleteRep/<repNum>")
@login_required
def deleteRep(repNum):
    # Get the task that needs to be deleted based on the id provided.

    try:
        rep.query.filter(rep.repNum == repNum).delete()
        # connect to the session and delete the task by id
        # commit changes to the database
        db.session.commit()
        # Once changes are made, update the homepage of the website
        return redirect("/repView")
    except Exception as e:
        # Print out an error
        print(f"ERROR:{e}")
        # Return an error as well, beause this function must return something.
        return f"ERROR:{e}"

# Logs out signed in admin
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

# Login page
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
    return render_template("login.html", error=None)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return admins.query.get(int(user_id))

# Unused, but allows the addition of new admin accounts
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if admins.query.filter_by(username=username).first():
            return render_template("sign_up.html", error="Username already taken!")

        hashed_password = generate_password_hash(
            password, method="pbkdf2:sha256")

        new_user = admins(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("sign_up.html")

# Main dashboard to navigate to database functions
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

# Updates customer credit limit based on name
@app.route("/creditUpdate", methods=["GET", "POST"])
@login_required
def updateCreditLimit():
    message = ""
    customers = customer.query.order_by(
        customer.customerName).all()  # Get all customers
    # get credit limit for each customer
    creditLim = customer.query.with_entities(
        customer.customerName, customer.creditLimit).all()

    if request.method == "POST":
        name = request.form.get("name")
        new_limit = request.form.get("credit")
        cust = customer.query.filter_by(customerName=name).first()
        if cust:
            message = f"Credit limit updated for {name} from ${cust.creditLimit} to ${new_limit}"
            cust.creditLimit = new_limit
            db.session.commit()
        else:
            message = f"Customer '{name}' not found"
    return render_template("update_credit.html", message=message, customers=customers, creditLim=creditLim)

# Routes to login page if user is unauthorized
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/")

# Takes file with SQL inserts and executes each insert
def insertFromFile():
    sql_file = open('inserts.sql', 'r')
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
                    if debugOutput:
                        print("Inserted object")
                # Assert in case of error
                except exc.IntegrityError as error:
                    if debugOutput:
                        print("Object already in database")
                # Finally, clear command string
                finally:
                    sql_command = ''

def ensureAdminIsPresent():
    # makes sure there is always at least the default admin account present on startup

    # hardcoded Admin info for simplicity. However, a function for securely registering and storing
    # a new admin is impemented above as register()
    defaultUsername = "Admin"
    defaultPassword = "supersecret" # very secret indeed XD
    foundDefaultUser = admins.query.filter_by(username=defaultUsername).first()

    hashedPassword = generate_password_hash(defaultPassword, method="pbkdf2:sha256")

    if not foundDefaultUser:
        addAdmin = insert(admins).values(
            username=defaultUsername, password=hashedPassword)
        db.session.execute(addAdmin)
        db.session.commit()
        print("Inserted default")

    elif foundDefaultUser and not check_password_hash(foundDefaultUser.password, defaultPassword):
        updateAdmin = update(admins)\
            .where(admins.username == "Admin")\
            .values(password=generate_password_hash(defaultPassword, method="pbkdf2:sha256"))
        db.session.execute(updateAdmin)
        db.session.commit()

#start the app itself running
if __name__ == "__main__" :
    debugOutput = False
    #Begins the database instance
    with app.app_context():
        db.create_all()
        insertFromFile()
        ensureAdminIsPresent()
    # Actually begins the program
    app.run(debug=debugOutput)