from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text # textual queries

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/anonfeedback")
def anonfeedback():
    return render_template("anonfeedback.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/tut")
def tut():
    return render_template("tut.html")

@app.route("/lecture")
def lecture():
    return render_template("lecture.html")

@app.route("/calender")
def calender():
    return render_template("calender.html")

@app.route("/resource")
def resource():
    return render_template("resource.html")

@app.route("/assignment")
def assignment():
    return render_template("assignment.html")

@app.route("/courseteam")
def courseteam():
    return render_template("courseteam.html")

if __name__ == "__main__":
    app.secret_key = b"secretkey"
    app.run(debug=True)