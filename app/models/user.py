from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from flask_login import UserMixin

from app.extensions import db
from app.extensions import login_manager


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_user(self, name, email, password):
        user = User(name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
    
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))