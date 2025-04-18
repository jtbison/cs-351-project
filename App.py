#Imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Table, Column, CHAR, DECIMAL, DATE, create_engine, insert, ForeignKey

#Creating a flask instance
app = Flask(__name__)
Scss(app)

#Initalize an instance of a database named "database"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

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
        return f"Task {self.repNum}"

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
    repNum = db.Column('RepNum', CHAR(2), ForeignKey(rep.repNum))

class orders(db.Model):
    __tablename__ = 'Orders'
    orderNum = db.Column('OrderNum', CHAR(3), primary_key=True)
    orderDate = db.Column('OrderDate', DATE)
    customerNum = db.Column('CustomerNum', CHAR(3))

class orderLine(db.Model):
    __tablename__ = 'OrderLine'
    orderNum = db.Column('OrderNum', CHAR(5), primary_key=True)
    itemNum = db.Column('ItemNum', CHAR(4), primary_key=True)
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

#Creating a table in SQLAlchemy API
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
        newRep = request.form["lastName"]
        # Create a new task object from the user input defined in current_task
        newTask = rep(lastName = newRep)
        #Attempt to connect to the database
        try:
            #connect to the database instance.
            db.session.add(newTask)
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

        stmt1 = insert(rep).values(repNum='99', lastName='Campos', firstName='Rafael', street="724 Vinca Dr.", city='Grove', state='CA', postalCode='90092', commission=23457.50, rate=0.06)
        stmt2 = insert(rep).values(repNum='30', lastName='Gradey', firstName='Megan', street='632 Liatris St.', city='Fullton', state='CA', postalCode='90085', commission=41317.00, rate=0.08)
        db.session.execute(stmt1)
        db.session.execute(stmt2)
        
    #Actually begins the program
    app.run(debug=True)
    db.session.commit()
    
