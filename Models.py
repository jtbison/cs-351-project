#Imports
from flask_login import UserMixin
from sqlalchemy import CHAR, DECIMAL, DATE, ForeignKey
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Database models
class admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"{self.id} {self.username} {self.password}"

class rep(db.Model):
    __tablename__ = 'rep'
    repNum = db.Column(CHAR(2), primary_key=True)
    lastName = db.Column(CHAR(15))
    firstName = db.Column(CHAR(15))
    street = db.Column(CHAR(15))
    city = db.Column(CHAR(15))
    state = db.Column(CHAR(2))
    postalCode = db.Column(CHAR(5))
    commission = db.Column(DECIMAL(7, 2))
    rate = db.Column(DECIMAL(3, 2))
    
    def __repr__(self) -> str:
        return self.firstName + self.lastName

class customer(db.Model):
    __tablename__ = 'customer'
    customerNum = db.Column(CHAR(3), primary_key=True)
    customerName = db.Column(CHAR(35), nullable=False)
    street = db.Column(CHAR(20))
    city = db.Column(CHAR(15))
    state = db.Column(CHAR(2))
    postalCode = db.Column(CHAR(5))
    balance = db.Column(DECIMAL(8, 2))
    creditLimit = db.Column(DECIMAL(8, 2))
    repNum = db.Column(ForeignKey("rep.repNum"))

class orders(db.Model):
    __tablename__ = 'orders'
    orderNum = db.Column(CHAR(3), primary_key=True)
    orderDate = db.Column(DATE)
    customerNum = db.Column(ForeignKey("customer.customerNum"))

class orderLine(db.Model):
    __tablename__ = 'orderLine'
    orderNum = db.Column(CHAR(5), ForeignKey("orders.orderNum"), primary_key=True)
    itemNum = db.Column(CHAR(4), ForeignKey("item.itemNum"), primary_key=True)
    numOrdered = db.Column(DECIMAL(6, 2))
    quotedPrice = db.Column(DECIMAL(6, 2))

class item(db.Model):
    __tablename__ = 'item'
    itemNum = db.Column(CHAR(4), primary_key=True)
    description = db.Column(CHAR(30))
    onHand = db.Column(DECIMAL(4, 0))
    category = db.Column(CHAR(3))
    storehouse = db.Column(CHAR(1))
    price = db.Column(DECIMAL(6, 2))
