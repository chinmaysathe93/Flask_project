from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#initialize MySQL
mysql = MySQL(app)

#INDEX
@app.route('/')
def index():
    return render_template('home.html')

#ABOUT
@app.route('/about')
def about():
    return render_template('about.html')

#ARTICLES
@app.route('/articles')
def article():
    #create cursor
    cur = mysql.connection.cursor()

    #get ARTICLES
    result = cur.execute("select * from articles")

    articles = cur.fetchall()

    if result>0:
        return render_template('articles.html',articles = articles)
    else:
        msg = 'No Articles found'
        return render_template('articles.html',msg=msg)
    cur.close()

#SINGLE ARTICLE
@app.route('/article/<string:id>/')
def article_id(id):
    #create cursor
    cur = mysql.connection.cursor()

    #get ARTICLES
    result = cur.execute("select * from articles where id = %s",[id])

    articles = cur.fetchone()

    return render_template('article.html',article=articles)

#REGISTER FORM CLASS
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min=1,max=50)])
    username = StringField('Username',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
        validators.EqualTo('confirm',message = 'Passwords do not Match')])
    confirm = PasswordField('Confirm Password')

#REGISTER
@app.route('/register',methods = ['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        #create DictCursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT into users(name,email,username,password) values (%s,%s,%s,%s)", (name,email,username,password))

        #commit toDB
        mysql.connection.commit()

        flash('You are now Registered and can log in','success')

        return redirect(url_for('index'))

    return render_template('register.html', form =form)

#user logging
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #creating a cursor
        cur = mysql.connection.cursor()

        #get user by Username
        result = cur.execute("SELECT * FROM users WHERE username =%s",[username])

        if result >0:
            #get stored hash password
            #fetchone -  fetches one or first from the database
            data = cur.fetchone()
            password = data['password']
            Authorname = data['name']
            EmailID = data['email']

            #comparing Passwords
            if sha256_crypt.verify(password_candidate,password):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = Authorname
                session['email'] = EmailID


                flash('You are Logged in','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html',error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html',error=error)
    return render_template('login.html')


#CHECK IF USER IS LOGGED INN
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Access, Please Login','danger')
            return redirect(url_for('login'))
    return wrap

#LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#DASHBOARD
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #create cursor
    cur = mysql.connection.cursor()

    #get ARTICLES
    result = cur.execute("select * from articles")

    articles = cur.fetchall()

    if result>0:
        return render_template('dashboard.html',articles = articles)
    else:
        msg = 'No Articles found'
        return render_template('dashboard.html',msg=msg)
    cur.close()
#Article form class
class ArticleForm(Form):
    title = StringField('Title',[validators.Length(min=1,max=200)])
    body = TextAreaField('Body',[validators.Length(min=30)])
#Add article route
@app.route('/add_article', methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        #create cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("insert into articles(title,body,author) Value (%s,%s,%s)",(title,body,session['name']))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Article Created','success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html',form=form)

#Edit article route
@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    #create cursor
    cur = mysql.connection.cursor()
    # get the article by id
    result = cur.execute("Select * from articles where id =%s",[id])
    article = cur.fetchone()

    #get form
    form = ArticleForm(request.form)

    #populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        #create cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("Update articles set title =%s,body=%s where id = %s",(title,body,id))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Article Edited','success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html',form=form)

#delete articles
@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
    #create cursor
    cur = mysql.connection.cursor()
    cur.execute("Delete from articles where id = %s",[id])

            #commit to DB
    mysql.connection.commit()

            #close connection
    cur.close()
    flash('Article Deleted','success')

    return redirect(url_for('dashboard'))
if __name__=='__main__':
#The session is unavailable because no secret key was set.
#Set the secret_key on the application to something unique and secret.
    app.secret_key ='secret123'
    app.run(debug=True)
