from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taut.db'  # Path to your SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define ORM models
class SessionHistory(db.Model):
    __tablename__ = 'session_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    started = db.Column(db.Integer, nullable=False)  # Unix timestamp
    stopped = db.Column(db.Integer, nullable=False)  # Unix timestamp
    parent_rating_key = db.Column(db.String, nullable=True)
    media_type = db.Column(db.String, nullable=False)

class SessionHistoryMetadata(db.Model):
    __tablename__ = 'session_history_metadata'
    rating_key = db.Column(db.String, primary_key=True)
    full_title = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)

# Example route
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/test_users')
def test_users():
    try:
        users = User.query.all()
        return f"Users: {[user.username for user in users]}"
    except Exception as e:
        return f"Error fetching users: {e}"


# Initialize the database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
