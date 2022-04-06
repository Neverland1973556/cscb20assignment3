
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import text # textual queries
import os

app = Flask(__name__)
secret_key = os.urandom(12).hex()
app.config['SECRET_KEY'] = secret_key
# set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///a3database.db'
# logout every 15 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
setIns = set()

# use person to record users
# typePerson indicate if it's student or Instructor
class Person(db.Model):
    __tablename__ = 'Person'
    Id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    username = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    # 0 is student, 1 is Instructor
    typePerson = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Person('{self.name}', '{self.email}', '{self.typePerson}')"

# schema for grades
class Evaluation(db.Model):
    __tablename__ = 'Evaluation'
    eid = db.Column(db.Integer, primary_key = True)
    stuMark = db.Column(db.Integer)
    remarkText = db.Column(db.String(200))

    student_username = db.Column(db.String(20), db.ForeignKey('Person.username'), nullable = False)
    typeName = db.Column(db.String(20), db.ForeignKey('Assignment.assignment_name'), nullable = False)
    total_mark = db.Column(db.Integer, db.ForeignKey('Assignment.total_mark'), nullable = False)
    stuName = db.Column(db.String(20), db.ForeignKey('Person.name'), nullable = False)

    def __repr__(self):
        return f"Evaluation('{self.typeName}', '{self.stuMark}')"

# schema for feedback
class Feedback(db.Model):
    __tablename__ = 'Feedback'
    fid = db.Column(db.Integer, primary_key = True)
    feedbackText = db.Column(db.String(200), nullable=False)
    instructor_username= db.Column(db.Integer, db.ForeignKey('Person.username'), nullable = False)

    def __repr__(self):
        return f"Feedback('{self.student_id}', '{self.instructor_id}')"

class Assignment(db.Model):
    __tablename__ = 'Assignment'
    aid = db.Column(db.Integer, primary_key = True)
    assignment_name = db.Column(db.String(20), nullable = False, unique=True)
    total_mark = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"Assignment('{self.assignment_name}', '{self.total_mark}')"

# home page, press home to go back here
@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
    return render_template("index.html")

# todo: if empty info or wrong info, flash
# register page
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        typePerson = request.form['typePerson']
        name = request.form['realName']
        username = request.form['Username']
        email = request.form['Email']

        if not name or not username or not email or not request.form['Password']:
            flash('Please enter the information required!', 'message')
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        
        if Person.query.filter_by(email = email).first():
            flash('Email address already existed! Please enter a new email!', 'error')
            return render_template('register.html')
        
        if Person.query.filter_by(username = username).first():
            flash('Username already existed! Please enter a new username!', 'error')
            return render_template('register.html')

        reg_details =(
            typePerson,
            # Id will be provided automatically by machine
            name,
            username,
            email,
            hashed_password
        )
        if typePerson == '0':
            add_students(reg_details)
            flash('Student Registration Successful! Please login now.')
        else:
            add_users(reg_details)
            flash('Instructor Registration Successful! Please login now.')
        return redirect(url_for('login'))

# login page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            flash('Already logged in!!')
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    else:
        username = request.form['Username']
        password = request.form['Password']
        person = Person.query.filter_by(username = username).first()
        if not person or not bcrypt.check_password_hash(person.password, password):
            flash('Please check your login details and try again!', 'error')
            return render_template('login.html')
        else:
            session['name'] = username
            # if int(typePerson) == 0:
            # # When it is a student
            #     setStu.add(username)
            if person.typePerson == 1:
                session['type'] = 1
            else:
                session['type'] = 0
            session.permanent = True
            return redirect(url_for('home'))

# logout page
@app.route('/logout')
def logout():
    session.pop('name', default = None)
    flash('You have successfully logged out! Now you can login or register!')
    return redirect(url_for('home'))

@app.route("/anonfeedback", methods = ['GET', 'POST'])
def anonfeedback():
    query_instructors_all = query_instructors()
    if request.method == 'GET':
        return render_template("anonfeedback.html", query_instructors_all = query_instructors_all)
    else:
        username = request.form['instructors']
        text_for_instructors = request.form['todo-input']
        feedback_details =(
            username,
            # Id will be provided automatically by machine
            text_for_instructors
        )
        add_feedbacks(feedback_details)
        flash('Feedback has been successfully added!')
        return redirect(url_for('anonfeedback'))

@app.route("/feedback", methods = ['GET', 'POST'])
def feedback():
    username = session['name']
    feedback_for_instructor = query_instructors_see(username)
    if request.method == 'GET':
         return render_template("feedback.html", feedback_for_instructor = feedback_for_instructor)
    # query_feedbacks_result

@app.route("/teacherGrade", methods = ['GET', 'POST'])
def teacherGrade():
    get_student_marks = query_all_student_marks()
    if request.method == 'GET':
        return render_template("teacherGrade.html", query_all_student_mark = get_student_marks)
    else:
        mark = request.form['stuMark']
        total_mark = request.form['total_mark']
        # student_marks = db.session.query(Evaluation).filter(Evaluation.student_username == username)
        if mark.isnumeric() != True or (int(mark) < 0):
            flash('Invalid grade, please check again!')
            return redirect(url_for('teacherGrade'))
        if float(mark) > float(total_mark):
            flash('Cannot exceed total mark, please check again!')
            return redirect(url_for('teacherGrade'))
        else:
            eid = request.form['eid']
            add_mark(mark, eid)
            flash('Mark has been successfully added!')
            return redirect(url_for('teacherGrade'))

@app.route("/evaluation", methods = ['GET', 'POST'])
def evaluation():
    username = session['name']
    student_marks = query_student_marks(username)
    if request.method == 'GET':
        return render_template("evaluation.html", query_student_marks = student_marks)
    else:
        text = request.form['remark_Text']
        if not text:
            flash('Please enter your remark request!')
            return redirect(url_for('evaluation'))
        else:
            eid = request.form['eid']
            add_remark_text(text, eid)
            flash('Remark request has been successfully added!')
            return redirect(url_for('evaluation'))

# information from assignment2
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



# helper function to add users to the database
def add_users(reg_details):
    instructor = Person(typePerson = reg_details[0], name = reg_details[1], username= reg_details[2], email = reg_details[3], password = reg_details[4])
    db.session.add(instructor)
    db.session.commit()

def add_students(reg_details):
    instructor = Person(typePerson = reg_details[0], name = reg_details[1], username= reg_details[2], email = reg_details[3], password = reg_details[4])
    db.session.add(instructor)
    # if it's a student, update the evaluation
    for assignment in db.session.query(Assignment).order_by(Assignment.aid): 
        mark = Evaluation(stuName = reg_details[1], stuMark = 0, student_username = reg_details[2], typeName = assignment.assignment_name, total_mark = assignment.total_mark)
        db.session.add(mark)
    db.session.commit()

    
def add_feedbacks(feedback_details):
    feedback = Feedback(instructor_username = feedback_details[0], feedbackText = feedback_details[1])
    db.session.add(feedback)
    db.session.commit()
    
def add_remark_text(text_to_remark, eid):
    db.session.query(Evaluation).filter(Evaluation.eid == eid ).update({'remarkText': text_to_remark})
    db.session.commit()

def add_mark(mark, eid):
    db.session.query(Evaluation).filter(Evaluation.eid == eid ).update({'stuMark': mark})
    db.session.commit()

def query_instructors():
    query_instructor = db.session.query(Person).filter(Person.typePerson == 1)
    return query_instructor

def query_instructors_see(username):
    query_instructor = db.session.query(Feedback).filter(Feedback.instructor_username == username)
    return query_instructor

def query_student_marks(username):
    student_marks = db.session.query(Evaluation).filter(Evaluation.student_username == username)
    return student_marks

def query_all_student_marks():
    student_marks = db.session.query(Evaluation)
    return student_marks

# def is_float_int(input: int) -> bool:
#     if not input.isalnum():
#         return False
#     elif input.isalpha():
#         return False



if __name__ == "__main__":
    app.run(debug=True)
