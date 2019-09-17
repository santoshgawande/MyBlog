from flask import Flask, render_template, flash, redirect, url_for, request, session, logging 
from data import Articles
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
app =Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 's'
app.config['MYSQL_DB'] = 'blog'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



Articles =Articles()
@app.route("/")
def main():
    return render_template("home.html") 
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles",methods=['GET','POST'])
def articles():
    return render_template("articles.html",articles=Articles)

@app.route("/article/<string:id>/")
def article(id):
    return render_template("article.html",id=id)

class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password',[
            validators.DataRequired(),
            validators.EqualTo('confirm',message ='Password do not match')
  ])
    confirm = PasswordField('Cornfirm Password')

@app.route("/register",methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name =form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur =mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,username,email,password) VALUES(%s,%s,%s,%s)",(name,username,email,password))
        mysql.connection.commit()
        cur.close()
        flash("You are registered..!!")
        redirect(url_for('main'))
#ireturn render_template('register.html',form=form)
    return render_template('register.html',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur =mysql.connection.cursor()
        result = cur.execute("SELECT * from users where username=%s",[username])
        if result > 0:
            data =cur.fetchone()
            dbpass = data['password']
            #enpassword = sha256_crypt.encrypt(password)
            if sha256_crypt.verify(password, dbpass):
            #if dbpass == enpassword :
                session['logged_in'] = True
                session['username'] = username
                flash("You are logged in","success")
                return redirect(url_for('dashboard'))
                #app.logger.info("Password matched..!")
                #error ="Password Matched"
                #return render_template("login.html")
            else:
                error ="Password Not Match"
                return render_template("login.html",error=error)
                #app.logger.info("Password is MisMatched")
            cur.close()
        else:
            #app.logger.info("NO User")
            error ="User doesn't exist"
            return render_template("login.html",error=error)

    return render_template("login.html")

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized User","error")
            return redirect(url_for('login'))
    return wrap

@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You are Logout ","Success")
    return redirect(url_for('login'))





if __name__ =='__main__':
    app.secret_key ='12345'
    app.run()

