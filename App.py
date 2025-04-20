#Imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, Table, Column, CHAR, DECIMAL, DATE, create_engine, insert, ForeignKey, select
from sqlalchemy.orm import Mapped, MappedColumn, relationship
from Models import customer, rep, orderLine, orders, item

#Creating a flask instance
app = Flask(__name__)
Scss(app)

#Initalize an instance of a database named "database"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

#Creating a table in SQLAlchemy API

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
def repPage():
#Function to add a task
    if request.method == "POST":
        #.form is refrencing the inputs in index.hml, under the form action.

        # Create a new task object from the user input defined in current_task

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

@app.route("/customerView", methods = ["POST", "GET"])
def customerPage():
    return render_template("customers", values=customer.query.all())

#Create the homepage of the webstie
@app.route("/", methods = ["POST","GET"])
def index():
    #Function to add a task
    if request.method == "POST":
        #.form is refrencing the inputs in index.hml, under the form action.
        current_task = request.form["content"]
        # Create a new task object from the user input defined in current_task
        newTask = MyTask(content = current_task)
        #Attempt to connect to the database
        try:
            #connect to the database instance.
            db.session.add(newTask)
            #commit changes to the database,
            db.session.commit()
            #Once the changes are made to the database, redirect the user to the updated homepage.
            return redirect("/")
        except Exception as e:
            #Print out an error
            print(f"ERROR:{e}")
            #Return an error as well, beause this function must return something.
            return f"ERROR:{e}"
    #Function to see all current tasks (it is an else becuase we always want the website to render with all database tasks shown.)
    else:
        #Sort the MyTask table by the data a task was created, save the value as tasks.
        tasks = MyTask.query.order_by(MyTask.created).all()
        #Render the website  IMPORTANT!!! in "tasks = tasks" the left tasks refers to "tasks" in idex.html, right tasks refers to "tasks" as defined above.
        return render_template("index.html", tasks = tasks)

def updateCreditLimit(name, newCreditLimit):
    cust = customer.query.get(name)
    cust.creditLimit = newCreditLimit
    db.session.commit()

@app.route("/report/")
def generateReport():
    
    #firstNames = select(rep.lastName, rep.firstName).select_from("rep").join("customer", rep.repNum == customer.repNum)
    firstNames = select(rep.lastName, rep.firstName, func.count(), func.sum(rep.repNum) / (func.count() + 1)).group_by(rep.lastName, rep.firstName)
    names = db.session.execute(firstNames)
  
    return render_template("report.html", repNames = names)

@app.route("/deleteRep/<repNum>")
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

#Page/fucntion to delete an item from the list.
@app.route("/delete/<int:id>")
def delete(id: int):
    #Get the task that needs to be deleted based on the id provided.
    delete_Task = MyTask.query.get_or_404(id)
    try:
        #connect to the session and delete the task by id
        db.session.delete(delete_Task)
        #commit changes to the database
        db.session.commit()
        #Once changes are made, update the homepage of the website
        return redirect("/")
    except Exception as e:
        #Print out an error
        print(f"ERROR:{e}")
        #Return an error as well, beause this function must return something.
        return f"ERROR:{e}"

#Page/fucntion to update an item from the list.
@app.route("/update/<int:id>", methods = ["GET","POST"])
def update(id:int):
    #Get the task that needs to be updated based on the id provided.
    task = MyTask().query.get_or_404(id)
    #if the method is for POSTing (This is a redundant step to ensure typing in the URL doesnt just do this anyway)
    if request.method == "POST":
        #set the content of the task with current id to the current value in the input form.
        task.content == request.form["content"]
        try:
            #Commit the updates to the database
            db.session.commit()
            #Update the homepage
            return redirect("/")
        except Exception as e:
            #Print out an error
            print(f"ERROR:{e}")
            #Return an error as well, beause this function must return something.
            return f"ERROR:{e}"    
    else:
        return "HOME"

#Page/function for logging into the database
@app.route("/login", methods=["GET", "POST"])
def login():
    # if(request.method = "POST"):
    #     return redirect("/")
    return render_template("login.html")

#start the app itself running
if __name__ in "__main__" :
   

    #Begins the databse instance
    with app.app_context():
        db.create_all()
        
        # inserts for testing
        
        #stmt1 = insert(rep).values(repNum='15', lastName='Campos', firstName='Rafael', street="724 Vinca Dr.", city='Grove', state='CA', postalCode='90092', commission=23457.50, rate=0.06)
        #stmt2 = insert(rep).values(repNum='30', lastName='Gradey', firstName='Megan', street='632 Liatris St.', city='Fullton', state='CA', postalCode='90085', commission=41317.00, rate=0.08)
        #stmt3 = insert(rep).values(repNum='45', lastName='Tian', firstName='Hui',street='1785 Tyler Ave.',city='Northfield',state='CA',postalCode='90098', commission=27789.25, rate=0.06)
        #stmt4 = insert(rep).values(repNum='60',lastName='Sefton', firstName='Janet', street='267 Oakley St.', city='Congaree', state='CA', postalCode='90097', commission=0.00, rate=0.06)
        #db.session.execute(stmt1)
        #db.session.execute(stmt2) 
        #db.session.execute(stmt3)
        #db.session.execute(stmt4)
        #db.session.commit()



        #VALUES  ('126','Toys Galore','28 Laketon St.','Fullton','CA','90085',1210.25,7500.00,'15');

        #VALUES ('260','Brookings Direct','452 Columbus Dr.','Grove','CA','90092',575.00,10000.00,'30');

        #VALUES ('334','The Everything Shop','342 Magee St.','Congaree','CA','90097',2345.75,7500.00,'45');

        #VALUES ('386','Johnson''s Department Store','124 Main St.','Northfield','CA','90098',879.25,7500.00,'30');

        #VALUES ('440','Grove Historical Museum Store','3456 Central Ave.','Fullton','CA','90085',345.00,5000.00,'45');
        

        #stmt1 = insert(customer).values('126','Toys Galore','28 Laketon St.','Fullton','CA','90085',1210.25,7500.00,'15')


    #Actually begins the program
    app.run(debug=True)
   
    
