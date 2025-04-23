#Imports
from flask import Flask, render_template, redirect, request, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func, text, CHAR, DECIMAL, DATE, ForeignKey, select

#Creating a flask instance
app = Flask(__name__)
Scss(app)

#Initalize an instance of a database named "database"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#Database models
class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

class rep(db.Model):
    __tablename__ = 'Rep'
    repNum = db.Column('RepNum', CHAR(2), primary_key=True)
    lastName = db.Column('LastName', CHAR(15))
    firstName = db.Column('FirstName', CHAR(15))
    street = db.Column('Street', CHAR(15))
    city = db.Column('City', CHAR(15))
    state = db.Column('State', CHAR(2))
    postalCode = db.Column('PostalCode', CHAR(5))
    commission = db.Column('Commision', DECIMAL(7, 2))
    rate = db.Column('Rate', DECIMAL(3, 2))
    
    def __repr__(self) -> str:
        return self.firstName + self.lastName

class customer(db.Model):
    __tablename__ = 'Customer'
    customerNum = db.Column('CustomerNum', CHAR(3), primary_key=True)
    customerName = db.Column('CustomerName', CHAR(35), nullable=False)
    street = db.Column('Street', CHAR(20))
    city = db.Column('City', CHAR(15))
    state = db.Column('State', CHAR(2))
    postalCode = db.Column('PostalCode', CHAR(5))
    balance = db.Column('Balance', DECIMAL(8, 2))
    creditLimit = db.Column('CreditLimit', DECIMAL(8, 2))
    repNum = db.Column('RepNum', ForeignKey("rep.repNum"))

class orders(db.Model):
    __tablename__ = 'Orders'
    orderNum = db.Column('OrderNum', CHAR(3), primary_key=True)
    orderDate = db.Column('OrderDate', DATE)
    customerNum = db.Column("CustomerNum", ForeignKey("customer.customerNum"))

class orderLine(db.Model):
    __tablename__ = 'OrderLine'
    orderNum = db.Column('OrderNum', CHAR(5), ForeignKey("orders.orderNum"), primary_key=True)
    itemNum = db.Column('ItemNum', CHAR(4), ForeignKey("item.itemNum"), primary_key=True)
    numOrdered = db.Column('NumOrdered', DECIMAL(6, 2))
    quotedPrice = db.Column('QuotedPrice', DECIMAL(6, 2))

class item(db.Model):
    __tablename__ = 'Item'
    itemNum = db.Column('ItemNum', CHAR(4), primary_key=True)
    description = db.Column('Description', CHAR(30))
    onHand = db.Column('OnHand', DECIMAL(4, 0))
    category = db.Column('Category', CHAR(3))
    storehouse = db.Column('Storehouse', CHAR(1))
    price = db.Column('Price', DECIMAL(6, 2))

class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(100), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"

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

#Create the homepage of the webstie
@app.route("/")
def index():
    return render_template("index.html")

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
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = Admins.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(int(user_id))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if Admins.query.filter_by(username=username).first():
            return render_template("sign_up.html", error="Username already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = Admins(username=username, password=hashed_password)
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
if __name__ in "__main__" :
   
    #Begins the databse instance
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

                    # Assert in case of error
                    except:
                        print('Ops')

                    # Finally, clear command string
                    finally:
                        sql_command = ''

    #Actually begins the program
    app.run(debug=True)
   
    
