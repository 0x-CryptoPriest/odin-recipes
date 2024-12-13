from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ideas.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    subscription_status = db.Column(db.Boolean, default=False)
    ideas = db.relationship('Idea', backref='author', lazy=True)
#1111
class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    ideas = Idea.query.all()
    return render_template('home.html', ideas=ideas)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/subscribe')
@login_required
def subscribe():
    current_user.subscription_status = True
    db.session.commit()
    flash('Successfully subscribed!')
    return redirect(url_for('home'))

@app.route('/share', methods=['GET', 'POST'])
@login_required
def share_idea():
    if request.method == 'POST':
        idea = Idea(
            title=request.form.get('title'),
            content=request.form.get('content'),
            user_id=current_user.id
        )
        db.session.add(idea)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('share.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database created successfully!")
        except Exception as e:
            print(f"Error creating database: {e}")
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=8080, debug=True) 