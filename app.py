from flask import Flask, request, flash, render_template, url_for, session, redirect
import os
from random import randint
import sqlite3 
import gc
from hashlib import sha512

from flask.templating import render_template
app = Flask(__name__)

ql=[]

@app.route('/')
@app.route('/index.html')
def index():
   return render_template('Index.html')


@app.route('/about-us.html')
def About():
   return render_template('About-us.html')

@app.route('/contact-us.html')
def Contact():
   return render_template('Contact-us.html')

@app.route('/features.html')
def Feature():
   return render_template('Features.html')

@app.route('/forgotpassword.html')
def Forgotpassword():
   return render_template('Forgot password.html')

@app.route('/login.html')
def Login():
   return render_template('Login.html')

@app.route('/registration.html')
def Register():
   return render_template('Registration.html')

@app.route('/startquiz',methods=['POST'])
def startquiz():
   Lev = request.form['Level']
   sub = request.form['Subject']
   clas = request.form['Class']
   global ql
   ql=[]
   con = sqlite3.connect('creds.db')
   c = con.cursor()
   subdict={'hist':'History','math':'Maths','sci':'Science'}
   qustndict={'hist':(1,21),'math':(1,21),'sci':(1,21)}
   l=[]
   for i in range(1,11):
      c.execute('select * from '+subdict[sub]+' where SI_NO='+str(i)+';')
      ql.append(c.fetchall()[0])
   con.close()
   
   
   return render_template('/question.html',ql=ql)


@app.route('/register', methods=["GET","POST"])
def reg_process():
   fname = request.form['fullname'] 
   p1 = request.form['passw']
   p2 = request.form['conpassw']
   if p1!=p2:
      return render_template('registration.html',msg='pdm') #pdm : password doesnt match
   
   em = request.form['email']
   con = sqlite3.connect('creds.db')
   c = con.cursor()
   c.execute("SELECT * FROM Rdetails WHERE email = '"+str(em)+"';")
   li = c.fetchall()
   print(li)
   if len(li) != 0:
      con.close()
      return render_template('registration.html', msg="ear")
   try:
      
      c.execute("INSERT INTO Rdetails (fullname,password,email) VALUES (?,?,?);", (fname,p1,em))
      con.commit()
   except:

      con.close()
      return render_template('registration.html', msg='sp') #server problem
   con.close()
   gc.collect()

   session['logged_in'] = True
   session['fname'] = fname
   return render_template('registration.html',msg='success')



      
      


@app.route('/login', methods=['POST'])
def log_process():
   if request.method=='POST':
      email = request.form['email']
      passw = request.form['passw']
      con = sqlite3.connect('creds.db')
      c = con.cursor()
      c.execute("SELECT * FROM Rdetails WHERE email = '"+str(email)+"' and password = '"+str(passw)+"'")
      dat = c.fetchall()
      con.close()
      print(dat)
      if dat ==[]:
         return render_template('login.html', msg='fail')
      else:
         return redirect('index.html')


@app.route('/feedback', methods=['POST'])
def forgotpassw_process():
   name = request.form['name']
   subject = request.form['subject']
   email = request.form['email']
   message = request.form['message']
   con = sqlite3.connect('creds.db')
   c = con.cursor()
   c.execute("INSERT INTO feedbacks (name,subject,email,message) VALUES (?,?,?,?);", (name,subject,email,message))
   con.commit()
   return render_template('contact-us.html',msg='success')


@app.route('/submitTest',methods=['POST'])
def submitTest():
   answers=[]
   global ql
   global username
   email='akshatakalashetty2001@gmail.com'
   sc=0
   nsc=0
   for i in range(len(ql)):
      try:
         answers.append(request.form['qustn'+str(i)])
         if answers[i]==ql[i][5].lower():
            sc+=1
         else:
            nsc+=1
      except:
         answers.append('0')
   con=sqlite3.connect('creds.db')
   c=con.cursor()
   c.execute('select tqs,tqsc from Rdetails where email="'+email+'";')
   dat=c.fetchall()[0]
   tqs = int(dat[0])+sc+nsc
   tqsc= int(dat[1])+sc

   c.execute('update Rdetails set  tqs='+str(tqs)+', tqsc='+str(tqsc)+' where email="'+email+'";')
   con.commit()
   con.close()
   return render_template('/final.html',ql=ql,noq=int(len(ql)),answers=answers, score=str(sc*4)+'/'+str(len(ql)*4))




@app.route('/doneWithTest')
def doneWithTest():
   return redirect(url_for('index'))




if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run()