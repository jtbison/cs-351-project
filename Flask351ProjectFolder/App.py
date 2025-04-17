#Imports
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Table, Column, CHAR, DECIMAL, DATE
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint


Base = declarative_base()
#Creating a flask instance
app = Flask(__name__)
Scss(app)

#Initalize an instance of a database named "databse"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

#Creating a table in SQLAlchemy API
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(100), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"

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
def delete(id:int):
    #Get the task that needs to be deleted based on the id provided.
    delete_Task = MyTask().query.get_or_404(id)
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


class rep(Base):
    column1 = Column('RepNum', CHAR(2), primary_key=True)
    column2 = Column('LastName', CHAR(15))
    column3 = Column('FirstName', CHAR(15))
    column4 = Column('Street', CHAR(15))
    column5 = Column('City', CHAR(15))
    column6 = Column('State', CHAR(2))
    column7 = Column('PostalCode', CHAR(5))
    column8 = Column('Commision', DECIMAL(7, 2))
    column9 = Column('Rate', DECIMAL(3, 2))

class customer(Base):
    __tableName__ = 'Customer'
    column1 = Column('CustomerNum', CHAR(3), primary_key=True)
    column2 = Column('CustomerName', CHAR(35), nullable=False)
    column3 = Column('Street', CHAR(20))
    column4 = Column('City', CHAR(15))
    column5 = Column('State', CHAR(2))
    column6 = Column('PostalCode', CHAR(5))
    column7 = Column('Balance', DECIMAL(8, 2))
    column8 = Column('CreditLimit', DECIMAL(8, 2))
    column9 = Column('RepNum', CHAR(2))

class orderLine(Base):
    __tableName__ = 'OrderLine'
    column1 = Column('OrderNum', CHAR(5))
    column2 = Column('ItemNum', CHAR(4))
    column3 = Column('NumOrdered', DECIMAL(6, 2))
    column4 = Column('QuotedPrice', DECIMAL(6, 2))

    __table_args__ = (
        PrimaryKeyConstraint('column1', 'column2')
    )

class orders(Base):
    __tableName__ = 'Orders'
    column1 = Column('OrderNum', CHAR(3))
    column2 = Column('OrderDate', DATE)
    column3 = Column('CustomerNum', CHAR(3))

#start the app itself running
if __name__ in "__main__" :
    #Begins the databse instance
    with app.app_context():
        db.create_all()
    #Actually begins the program
    app.run(debug=True)