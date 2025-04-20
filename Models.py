from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Table, Column, CHAR, DECIMAL, DATE, create_engine, insert, ForeignKey, select
from sqlalchemy.orm import Mapped, MappedColumn, relationship

db = SQLAlchemy()

