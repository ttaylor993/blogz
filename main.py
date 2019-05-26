from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:12345@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '05241951'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref ='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
        
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
                       
        if not username:
            flash("You Must Enter a User Name")
            return redirect('/login') 
                
        if not password:
            flash("You Must Enter a Valid Password")
            return redirect('/login')
        elif len(password) < 5:
            flash("Your password must be at least 5 characters long")
            return redirect('/login')
        else:
            num_in_password = False
            for x in password:
                if x.isdigit():
                    num_in_password = True
            if not num_in_password:
                flash("Your password must contain at least one number")
                return redirect('/login')
                
        for char in password:
            if char == " ":
                flash("Your password cannot contain a blank space")
                return redirect('/login')
                                             
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    return render_template('login.html')  

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
       
        if len(username) < 3 or len(username) > 20:
            flash("You must enter a user name 3 characters or longer and shorter than 21")
            return redirect('/signup') 
        for char in username:
            if char == " ":
                flash("Your user name cannot contain a blank space")
                return redirect('/signup')

        if not verify:
            flash("You must re-enter your password")
            return redirect('/signup')
        if password != verify:
            flash("Your 2nd entry did not match your 1st password")
            return redirect('/signup')
           
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            error = "Duplicate user"
            return render_template('signup.html', error=error)

    return render_template('signup.html')


@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    error = None

    owner = User.query.filter_by(username=session['username']).first()

    if request.method =='POST':
        new_title = request.form['title']
        new_body = request.form['body']
        blogs = Blog.query.filter_by(owner=owner).all() 
        new_post = Blog(new_title, new_body, owner)
        if not new_title or not new_body:
            error = "Enter a blog title and a blog post"
            return render_template('newpost.html', error=error)   
        else:
            db.session.add(new_post)
            db.session.commit()
    
    return render_template('newpost.html') 

@app.route('/newblog')
def newblog():
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    blogs = Blog.query.all()
   
    return render_template('newblog.html', blog=blog)
    
@app.route('/', methods =['POST', 'GET'])
def index():
    users = User.query.all()     
    return render_template('index.html', title='Posted Users!', users=users) 

@app.route('/singleUser')
def singleUser():
    users = User.query.filter_by(username=session['username']).first()
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    blogs = Blog.query.filter_by(owner=users)
    return render_template('singleUser.html', users=users, blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')    

if __name__ =="__main__":
    app.run()  