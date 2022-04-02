from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text # textual queries

app = Flask(__name__)
# what is this?
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///a3database.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# todo: change to our own type
class Instructor(db.Model):
    __tablename__ = 'Person'
    pId = db.Column(db.Integer, primary_key = True)
    pName = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return f"Person('{self.username}', '{self.email}')"

class Student(db.Model):
    __tablename__ = 'Student'
    stuId = db.Column(db.Integer, primary_key = True)
    stuName = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), nullable = False, unique=True)
    password = db.Column(db.String(20), nullable = False)
    email = db.Column(db.String(20), unique=True, nullable=False)

    # foreign key, need to change
    person_id = db.Column(db.Integer, db.ForeignKey('Person.id'), nullable = False)

    def __repr__(self):
        return f"Student('{self.stuName}', '{self.email}')"

class Evaluation(db.Model):
    __tablename__ = 'Evaluation'
    eid = db.Column(db.Integer, primary_key = True)
    typeName = db.Column(db.String(20), nullable = False, unique=True)
    totalMark = db.Column(db.Integer)
    stuMark = db.Column(db.Integer)
    remarkReq = db.Column(db.Boolean)
    remarkText = db.Column(db.String(200), nullable=False)

    # foreign key, need to change
    student_id = db.Column(db.Integer, db.ForeignKey('Student.stuId'), nullable = False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Instructor.stuId'), nullable = False)

    def __repr__(self):
        return f"Evaluation('{self.typeName}', '{self.stuMark}')"

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    fid = db.Column(db.Integer, primary_key = True)
    feedbackText = db.Column(db.String(200), nullable=False)

    # foreign key, need to change
    student_id = db.Column(db.Integer, db.ForeignKey('Student.stuId'), nullable = False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('Instructor.stuId'), nullable = False)

    def __repr__(self):
        return f"Evaluation('{self.student_id}', '{self.instructor_id}')"

@app.route("/")
@app.route("/home")
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