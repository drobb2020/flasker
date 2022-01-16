import os
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from forms import NamerForm, PasswordForm, PostForm, UserForm, LoginForm

app = Flask(__name__)
# Old DB
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
# New DB

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:Excess10n@localhost/flasker"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(
                username=form.username.data,
                name=form.name.data,
                email=form.email.data,
                password_hash=hashed_pw
                )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        flash("Your account is successfully created.", 'success')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users, title='Add User')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully.", 'success')
            return render_template('update.html', form=form, name_to_update=name_to_update, title='Update')
        except:
            flash("User update failed. Try again.", 'warning')
            return render_template('update.html', form=form, name_to_update=name_to_update, title='Update')
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, title='Update')


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully.", 'success')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', 
                               form=form, 
                               name=name, 
                               our_users=our_users, 
                               title='Add User')
    except:
        flash("There was a problem deleting the user.", 'warning')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', 
                               form=form, 
                               name=name, 
                               our_users=our_users, 
                               title='Add User')


# Login Page --------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login successful.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password. Please try again.', 'warning')
        else:
            flash('That user does not exist. Check your username', 'warning')
    return render_template('login.html', form=form, title='Login')


# Dashboard Page --------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully.", 'success')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, title='Update')
        except:
            flash("User update failed. Try again.", 'warning')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, title='Update')
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, title='Update')
    return render_template('dashboard.html', title='Dashboard')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    first_name = 'David'
    return render_template('index.html', first_name=first_name, title='Home')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, title='User')


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Your name has been submitted successfully.", 'success')
    return render_template('name.html', name=name, form=form, title='Name')


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_to_check.password_hash, password)
        # flash("Your name has been submitted successfully.", 'success')
    return render_template('test_pw.html',
                           email=email, 
                           password=password, 
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form, 
                           title='Test Password')


@app.route('/add_post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # Add post to database
        db.session.add(post)
        db.session.commit()
        flash('Your post submitted successfully.', 'success')
    return render_template('add_post.html', form=form, title="Add Post")


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.content = form.content.data
        post.slug = form.slug.data
        db.session.add(post)
        db.session.commit()
        flash('Your post was successfully updated.', 'success')
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.content.data = post.content
    form.slug.data = post.slug
    return render_template('edit_post.html', form=form, title="Edit Post")


@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Your post has been deleted successfully.', 'success')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts, title="Posts")
    except:
        flash('Your post could not be deleted, please try again.', 'danger')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts, title="Posts")


@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts, title="Posts")


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post, title="Post")


@app.route('/pizza')
def get_favorite_pizza():
    favorite_pizza = {
        "David": "Canadian",
        "John": "Combination",
        "Andrew": "Hawaiian",
        "Bill": "Pepperoni"
    }
    return favorite_pizza


@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.errorhandler(404)
def page_not_fount(error):
    return render_template('errors/404.html', title='Page not Found'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html', title='Internal Server Error'), 500
