from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Table, Column, CHAR, DECIMAL, DATE, create_engine, insert, ForeignKey, select
from sqlalchemy.orm import Mapped, MappedColumn, relationship

db = SQLAlchemy()

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

    customers = db.relationship("customer", back_populates="rep")
    
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
    repNum = db.relationship('RepNum', db.ForeignKey("rep.repNum"))

    orders = db.relationship("orders", backref="customer")

class orders(db.Model):
    __tablename__ = 'Orders'
    orderNum = db.Column('OrderNum', CHAR(3), primary_key=True)
    orderDate = db.Column('OrderDate', DATE)
    customerNum = db.Column("CustomerNum", CHAR(3), db.ForeignKey("customer.customerNum"))

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