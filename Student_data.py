from flask import Flask ,render_template,request,redirect,url_for,flash,abort,session,jsonify,g
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.dialects.sqlite
import os.path
import json
import matplotlib.pyplot as plt
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = 'Subham'

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Student_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db = SQLAlchemy(app)

#sender email_password
if os.path.exists('email.json'):
    with open('email.json') as email_file:
        email_data = json.load(email_file)
        sender_email=email_data["sender_email"]
        sender_password=email_data["sender_password"]

app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = sender_email
app.config['MAIL_PASSWORD'] = sender_password
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = True

mail= Mail(app)

class Studentdatabase(db.Model):
    roll_no = db.Column(db.Integer,primary_key=True)
    student_name= db.Column(db.String(3000),nullable=False)
    maths = db.Column(db.Integer,nullable=False)
    physics = db.Column(db.Integer,nullable=False)
    chemistry = db.Column(db.Integer,nullable=False)
    total_marks = db.Column(db.Integer,nullable=False)
    teacher_name=db.Column(db.Integer,nullable=False)
    student_email=db.Column(db.String(30),nullable=False)

    def __init__(self,roll_no,student_name,maths,physics,chemistry,total_marks,teacher_name,student_email):
        self.roll_no=roll_no
        self.student_name=student_name
        self.maths=maths
        self.physics=physics
        self.chemistry=chemistry
        self.total_marks=total_marks
        self.teacher_name=teacher_name
        self.student_email=student_email

@app.before_request
def before_request():
   g.username = None
   if 'username' in session:
       g.username = session['username']

@app.route('/')
def index():
    if g.username:
       return render_template('index.html',name=g.username)
    else:
       return render_template('login.html')

@app.route('/login', methods =['GET', 'POST'])
def login():
    if g.username:
        flash('You already logged in!')
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
        
            if os.path.exists('login_data.json'):
                with open('login_data.json') as login_file:
                    logins = json.load(login_file)
        
            if email not in logins.keys():
                redirect(url_for('sign_up'))
                flash("Account doesn't exits. Please create a account")
            elif logins[email]['password']==password:
                session['loggedin'] = True
                session['username'] = logins[email]['username']
                session['email']=email
                flash('Logged in successfully !')
                return redirect(url_for('index'))
            else:
                flash("Incorrect password")
    return render_template('login.html')

@app.route('/sign_up', methods =['GET', 'POST'])
def sign_up():
    log={}
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if os.path.exists('login_data.json'):
            with open('login_data.json') as login_file:
                logins = json.load(login_file)
        
        if email in logins.keys():
            redirect(url_for('login'))
            flash("Account is already exists.Please log in")
        else:
            log[email] = {'username':username,'password':password}
            log.update(logins)
            with open('login_data.json','w') as login_file:
                json.dump(log,login_file)
                #session[request.form['message_en']]=True
                flash("Account is created successfully Please log in")
    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/Student',methods = ['POST', 'GET'])
def Student():
    if request.method == 'POST':
        roll_no=request.form['roll']
        student_name=request.form['student_name']
        maths=request.form['maths']
        physics=request.form['physics']
        chemistry=request.form['chemistry']
        student_email=request.form['student_email']
        total_marks=int(maths)+int(physics)+int(chemistry)
        teacher_name=session['username']
        
        check= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll_no).first())
        
        if check:
            flash('That Roll number has already been existed. Please use another Roll number')
        else:
            entry=Studentdatabase(roll_no,student_name,maths,physics,chemistry,total_marks,teacher_name,student_email)
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

@app.route('/get_data', methods =['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        roll = request.form['roll_no']
        check= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll).first())
        if check:
            dshow=db.session.query(Studentdatabase).filter_by(roll_no=roll).first()
            return render_template('get_show_data.html',dshow=dshow)
            #flash("Data for roll = "+roll+" is succesfully deleted from database")    
        else:
            flash("That Roll number did'nt exists")
    return render_template('get_data.html')

@app.route('/get_show_data', methods =['GET', 'POST'])
def get_show_data():
    return render_template('get_show_data.html')

@app.route('/compare_data', methods =['GET', 'POST'])
def compare_data():
    if request.method == 'POST':
        roll1 = request.form['roll1']
        roll2 = request.form['roll2']
        check1= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll1).first())
        check2= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll2).first())
        if check1 and check2:
            student1=db.session.query(Studentdatabase).filter_by(roll_no=roll1).first()
            student2=db.session.query(Studentdatabase).filter_by(roll_no=roll2).first()
            #list for graph
            rolls=[roll1,roll2]
            names=[]
            tol_marks=[]
            m_marks=[]
            p_marks=[]
            c_marks=[]
            #append
            names.append(student1.student_name)
            tol_marks.append(student1.total_marks)
            m_marks.append(student1.maths)
            p_marks.append(student1.physics)
            c_marks.append(student1.chemistry)

            names.append(student2.student_name)
            tol_marks.append(student2.total_marks)
            m_marks.append(student2.maths)
            p_marks.append(student2.physics)
            c_marks.append(student2.chemistry)

            #plot
            plt.subplot(2,2,1)
            plt.bar(names,m_marks,label=rolls)
            plt.xlabel('names of students')
            plt.ylabel('math marks')
            plt.legend()
            plt.subplot(2,2,2)
            plt.bar(names,p_marks,label=rolls)
            plt.xlabel('names of students')
            plt.ylabel('physics marks')
            plt.legend()
            plt.subplot(2,2,3)
            plt.bar(names,c_marks,label=rolls)
            plt.xlabel('names of students')
            plt.ylabel('chemistry marks')
            plt.legend()
            plt.subplot(2,2,4)
            plt.bar(names,tol_marks,label=rolls)
            plt.xlabel('names of students')
            plt.ylabel('total marks')
            plt.legend()
            plt.savefig('static/my_plot.png')
            #plt.clf()
            plt.close(plt.clf())
    
            return render_template('show_compare.html',roll1=roll1,roll2=roll2,url ='static/my_plot.png')
            #flash("Data for roll = "+roll+" is succesfully deleted from database")    
        elif check1:
            flash("This Roll number=" + roll2 + " did'nt exists")
        elif check2:
            flash("This Roll number=" + roll1 + " did'nt exists")
        else:
            flash("both roll number="+ roll1 +" and "+ roll2 +" didn't exists")
    return render_template('compare_data.html')

@app.route('/compare_all', methods =['GET', 'POST'])
def compare_all():
    #result = SomeModel.query.with_entities(SomeModel.col1, SomeModel.col2)
    #names = db.session.query(Studentdatabase.student_name)
    #tol_marks = db.session.query(Studentdatabase).with_entities(Studentdatabase.total_marks)
    #p_marks = db.session.query(Studentdatabase).with_entities(Studentdatabase.physics)
    #c_marks = db.session.query(Studentdatabase).with_entities(Studentdatabase.chemistry)
    #m_marks = db.session.query(Studentdatabase.maths)
    #rolls = db.session.query(Studentdatabase).with_entities(Studentdatabase.roll_no)
    studentdata=Studentdatabase.query.all()
    names=[]
    m_marks=[]
    c_marks=[]
    p_marks=[]
    tol_marks=[]
    rolls=[]
    for student in studentdata:
        names.append(student.student_name)
        m_marks.append(student.maths)
        c_marks.append(student.chemistry)
        p_marks.append(student.physics)
        tol_marks.append(student.total_marks)
        rolls.append(student.roll_no)

    plt.subplot(2,2,1)
    plt.bar(names,m_marks)
    plt.xlabel('names of students')
    plt.ylabel('math marks')
    plt.legend()
    plt.subplot(2,2,2)
    plt.bar(names,p_marks)
    plt.xlabel('names of students')
    plt.ylabel('physics marks')
    plt.legend()
    plt.subplot(2,2,3)
    plt.bar(names,c_marks)
    plt.xlabel('names of students')
    plt.ylabel('chemistry marks')
    plt.legend()
    plt.subplot(2,2,4)
    plt.bar(names,tol_marks)
    plt.xlabel('names of students')
    plt.ylabel('total marks')
    plt.legend()
    plt.savefig('static/plot_all.png')
    #plt.clf()
    #plt.savefig('plot_all.png')
    plt.close(plt.clf())
    
    l=len(names)
    return render_template('compare_all.html',l=l,names=names,rolls=rolls,url ='static/plot_all.png')


@app.route('/show_compare', methods =['GET', 'POST'])
def show_compare():
    return render_template('show_compare.html')


@app.route('/email_sent', methods =['GET', 'POST'])
def email_sent():
    if request.method == 'POST':
        roll=request.form['roll']
        check= bool(db.session.query(Studentdatabase).filter_by(roll_no=roll).first())
        if check:
            d=db.session.query(Studentdatabase).filter_by(roll_no=roll).first()
            msg = Message('Result of test', sender = sender_email , recipients = [d.student_email])
            msg.body = "Hello "+d.student_name+"\n your marks:\n Physics:"+str(d.physics)+"\n Chemistry:"+str(d.chemistry)+"\n Maths:"+str(d.maths)+"\n Total:"+str(d.total_marks)+"For more details contact "+d.teacher_name
            mail.send(msg)
            flash('Mail sent succesfully')
        else:
            flash("roll doesn't found")
    return render_template('email_sent.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('pagenotfound.html'),404

if __name__=="__main__":
    app.run (debug=True)