
from datetime import date
from os import name
from MySQLdb import cursors, paramstyle
from flask import Flask, config,render_template,flash,redirect,request, session,json
from flask_login.utils import _secret_key 
from flask_mysqldb import MySQL
from flask_login import UserMixin
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key="SHA256"



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'recruit-me'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shashi22'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
db = MySQL(app)

with open('config.json','r') as c:
    params=json.load(c)["params"]


@app.route('/',methods=['POST','GET'])

def home():
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['name']
        telnum=userDetails['telnum']
        email=userDetails['email']
        msg=userDetails['msg']
        cur=db.connection.cursor()
        cur.execute("INSERT INTO message(name,telnum,email,msg) VALUES(%s,%s,%s,%s)",(name,telnum,email,msg))
        db.connection.commit()
        cur.close()
        return redirect('/')


    return render_template('index.html')


@app.route('/register',methods=['POST','GET'])

def register():
    if request.method=='POST':
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        telnum=userDetails['telnum']
        password= userDetails['password']
        encpas=generate_password_hash(password)
        cur=db.connection.cursor()
        cur.execute("INSERT INTO users(name,email,telnum,password) VALUES(%s,%s,%s,%s)",(name,email,telnum,encpas))
        db.connection.commit()
        cur.close()
        flash("Registration successful..","info")
        return redirect('/')

    return render_template('register.html')   



@app.route('/login',methods=['POST','GET'])

def login():
    msg=''
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        cur=db.connection.cursor()
        if cur.execute('SELECT * from users WHERE email=%s',[email]):
            record=cur.fetchone()
            print(record)
            if check_password_hash(record['password'],password):
                if record:
                    session['loggedin']=True
                    session['uid']=record['uid']
                    session['username']=record['name']

                    return redirect('/jobs')
            else:
                msg = 'Incorrect Password!'
        else:
            msg='Incorrect email'
    return render_template('login.html',msg=msg)

@app.route('/logout')
def clr():
    session.clear()



@app.route('/admin',methods=['POST','GET'])

def admin():
    msg=''
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        if(email==params['email'] and password==params['password']):
            session['email']=email
            return redirect("/joboperation")
        else:
            msg= 'Incorrect credential'
    return render_template("loginadmin.html",msg=msg)
    
       

@app.route('/joboperation',methods=['POST','GET'])
def jobop():
        
       
    cur=db.connection.cursor()   
    cur.execute("SELECT *from job ")
    data=cur.fetchall()
    # print(data)
    return render_template('joboperation.html',value=data)
        


         
@app.route('/jobs',methods=['POST','GET'])
def jobs():
             cur=db.connection.cursor()   
             cur.execute("SELECT *from job ")
             data=cur.fetchall()
             return render_template('jobs.html',value=data)



    


@app.route('/addjob',methods=['POST','GET'])  
def addjobs():
    cur=db.connection.cursor()   
    if request.method=='POST':        
        userDetails=request.form
        jobrole=userDetails['jobrole']
        jobtype=userDetails['jobtype']
        joblocation=userDetails['joblocation']
        salary=userDetails['salary']
        jobdesc=userDetails['jobdesc']
         
        cur.execute("INSERT INTO job(jobrole,jobtype,joblocation,salary,jobdesc)VALUES(%s,%s,%s,%s,%s)",(jobrole,jobtype,joblocation,salary,jobdesc))
        db.connection.commit()
     
        return redirect('/joboperation')
    cur.close()

    return render_template('addjob.html')

@app.route('/deletejob/<string:jid>',methods=['POST','GET'])
def deletejobs(jid):
    cur=db.connection.cursor()  
    if request.method=='POST':
         cur.execute("DELETE from job  Where jobid =%s",(str(jid),))
         db.connection.commit()
         return redirect('/joboperation')
    cur.close()    

    return render_template('deletejob.html',value=jid)


@app.route('/appliedjobs',methods=['POST','GET'])
def appliedjobs():
      
       cur=db.connection.cursor()   
       print(session)
       cur.execute('SELECT * from job WHERE jobid IN(SELECT jobid from appliedjobs WHERE uid=%s)',(str(session['uid']),))
       data=cur.fetchall()
       return render_template('appliedjobs.html',value=data)





@app.route('/confirm/<string:jid>/<string:uid>',methods=['POST','GET'])  
def confirm(jid,uid):
    cur=db.connection.cursor() 
    uid=str(uid)
    jobid=str(jid)
    if request.method=='POST':        
       
        cur.execute("INSERT INTO confirmedjobs(uid,jobid)VALUES(%s,%s)",(uid,jobid))
        db.connection.commit()
        return redirect('/appliedjobsadmin')
    cur.close()


    
    return render_template('confirm.html',value=jid,uid=uid)


   
@app.route('/confirmedjobs',methods=['POST','GET'])
def confirmedjobs():
      cur=db.connection.cursor()   
      cur.execute('SELECT * from job WHERE jobid IN(SELECT jobid from confirmedjobs WHERE uid=%s)',(str(session['uid']),))
      data=cur.fetchall()
   
      return render_template('confirmedjobs.html',value=data)
 


@app.route('/appliedjobsadmin',methods=['POST','GET'])
def appliedjobsadmin(): 
             cur=db.connection.cursor()   
             cur.execute('SELECT * from job j,users u,appliedjobs aj where j.jobid=aj.jobid and u.uid=aj.uid')
             data=cur.fetchall()
             print(len(data))
             return render_template('appliedjobsadmin.html',value=data)





@app.route('/applyjob/<string:jid>',methods=['POST','GET'])  
def applyjob(jid):
    cur=db.connection.cursor() 
    uid=str(session['uid'])
    jobid=str(jid)
    if request.method=='POST':        
        userDetails=request.form
        qualification=userDetails['qualification']
        experinces=userDetails['experinces']
       
        cur.execute("INSERT INTO appliedjobs(uid,jobid,qualification,experinces)VALUES(%s,%s,%s,%s)",(uid,jobid,qualification,experinces))
        db.connection.commit()
        return redirect('/jobs')
    cur.close()

    return render_template('resume.html',value=jid)

if __name__ == "__main__":
    app.run(debug=True)








    