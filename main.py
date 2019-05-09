from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '05241951'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body
  
@app.route('/newpost', methods = ['POST', 'GET'])
def newpost():
    error = None

    if request.method =='POST':
        new_title = request.form['title']
        new_body = request.form['body']
        new_post = Blog(new_title, new_body)
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
    blogs = Blog.query.all()     
    return render_template('blog.html', title='Build a Blog!', blogs=blogs) 

if __name__ =="__main__":
    app.run()  