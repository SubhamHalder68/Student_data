from flask import Flask ,render_template,request,redirect,url_for,flash,abort,session,jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite
from sqlalchemy import text


app = Flask(__name__)
app.secret_key = 'Subham'

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Student_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db = SQLAlchemy(app)

class Studentdatabase(db.Model):
    roll_no = db.Column(db.Integer,primary_key=True)
    student_name= db.Column(db.String(3000),nullable=False)
    maths = db.Column(db.Integer,nullable=True)
    physics = db.Column(db.Integer,nullable=True)
    chemistry = db.Column(db.Integer,nullable=True)
    total_marks = db.Column(db.Integer,nullable=True)

    def __init__(self,roll_no,student_name,maths,physics,chemistry,total_marks):
        self.roll_no=roll_no
        self.student_name=student_name
        self.maths=maths
        self.physics=physics
        self.chemistry=chemistry
        self.total_marks=total_marks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Student',methods = ['POST', 'GET'])
def Student():
    if request.method == 'POST':
        roll_no=request.form['roll']
        student_name=request.form['name']
        maths=request.form['maths']
        physics=request.form['physics']
        chemistry=request.form['chemistry']
        total_marks=int(maths)+int(physics)+int(chemistry)
        
        check= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll_no).first())
        
        if check:
            flash('That Roll number has already been existed. Please use another Roll number')
        else:
            entry=Studentdatabase(roll_no,student_name,maths,physics,chemistry,total_marks)
            db.session.add(entry)
            db.session.commit()
            flash('Data Entered succesfully')
    return render_template('Student.html')
  
@app.route('/student_data_show')
def student_data_show():
    studentdata=Studentdatabase.query.all()
    return render_template('student_data_show.html',studentdata=studentdata)
    
@app.route('/delete_data',methods = ['POST', 'GET'])
def delete_data():
    if request.method == 'POST':
        roll=request.form['roll']
        check= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll).first())
        if check:
            d=db.session.query(Studentdatabase).filter_by(roll_no=roll).first()
            db.session.delete(d)
            db.session.commit()
            flash("Data for roll = "+roll+" is succesfully deleted from database")    
        else:
            flash("That Roll number did'nt exists")
    return render_template('delete_data.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('pagenotfound.html'),404

if __name__=="__main__":
    app.run (debug=True)