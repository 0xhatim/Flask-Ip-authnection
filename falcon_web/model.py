from email.policy import default
from itsdangerous import TimedJSONWebSignatureSerializer as Ser
from datetime import datetime
from falcon_web import db,login_manager,app# impore each other in same time ! so don't // so we change it to main
from flask_login import UserMixin
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='back.gif')
    instagram_user = db.Column(db.String(200), default=None)
    ip_active_proxies = db.Column(db.String(200), default=None)
    password = db.Column(db.String(60), nullable=False)
    regster_time = db.Column(db.String(60),default=str(datetime.datetime.now()))
    def get_reset_token(self,expires_sec=1800):
        s = Ser(app.config["SECRET_KEY"],expires_sec)
        return s.dumps({"user_id":self.id}).decode("utf-8")
    
    @staticmethod
    def verify_reset_token(token):
        s = Ser(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.String(120),unique=True, nullable=True)
    state = db.Column(db.Boolean())





