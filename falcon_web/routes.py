from flask import render_template, url_for, flash, redirect,request
import os
from PIL import Image
from falcon_web import app,db,bcrypt ,mail# make db then import 
from falcon_web.form import *# package name then model
from falcon_web.model  import User,Register
from flask_login import login_user,current_user,logout_user,login_required
from werkzeug.utils import secure_filename
import secrets
from flask import send_file
from flask_mail import Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
"""
    MAIN WEBSITE SETTING

"""
@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/home_admin")
def home_admin():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            my_list = db.session.query(User).all()
            return render_template("admin_index.html",my_list=my_list)
    
    return redirect(url_for('home'))
@app.route("/code_maker", methods=['GET', 'POST'])
def code_maker():
    if current_user.is_authenticated:
        if current_user.username == 'admin':
            form = code_generationr()
            if form.validate_on_submit():
                try:
                    code_made = Register(coupon_id=form.code_filed.data)
                    db.session.add(code_made)
                    db.session.commit()
                    flash(f"Made Succcessufly {form.code_filed.data}",'success')

                except:
                    flash("its already made",'danger')
            return render_template("maker_code.html",form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user_check = User.query.filter_by(email=form.email.data).first()# get the same email
        user_check_by_user = User.query.filter_by(username=form.email.data).first()# get the same email

        if user_check and bcrypt.check_password_hash(user_check.password,form.password.data):#get the same password of email and they written

            login_user(user_check,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))# %2 account , u need to login then u go to it
        elif user_check_by_user and bcrypt.check_password_hash(user_check_by_user.password,form.password.data):#get the same password of email and they written

            login_user(user_check_by_user,remember=form.remember.data)
            if form.email.data == 'admin':
                return redirect(url_for('home_admin'))

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))# %2 account , u need to login then u go to it
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        code_reg = form.register_code.data
        q = db.session.query(Register).filter(Register.coupon_id==code_reg).first()
        try:
            print('COPON ID ',q.coupon_id,'Enterd',code_reg,'q.state:',q.state)
            if q.coupon_id == code_reg and q.state == False or q.state == None:
                user = User(username=form.username.data,email=form.email.data,password=hashed_password)
                db.session.add(user)
                q.state = True
                db.session.commit()
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('login'))#41dad5c341
            else:
                flash(f'Invalid Code Register ', 'danger')
                print("invalid code")


        except:
            flash(f'Invalid Code Register ', 'danger')
            print("invalid code")

    return render_template('register.html', title='Register', form=form)





def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset | تغيير كلمه مرور",
        sender="mexaw0bot@gmail.com",
        recipients=[user.email])
    msg.body = f''' 
    
    To reset your password , open the following link:


    {url_for('reset_token',token=token,_external=True)}



    If you did not make this requests , just ignore it :) 
    Any Question @31412.bye | @mexaw

    
    '''
    try:

        mail.send(msg)
    except Exception as e:
        print(e)

@app.route("/active_link",methods=["GET"])
@limiter.exempt
def api_mexaw():
    my_list = db.session.query(User).all()
    return render_template('api.html',my_list=my_list)

@app.route("/reset_password",methods=["GET","POST"])
def reset_request():
    try:

        if current_user.is_authenticated:
            return redirect(url_for('login'))
        form = RequestsResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            send_reset_email(user)
            flash("An email has been sent with link","info")
            return redirect(url_for("login"))
    except:
        flash("error","danger")

    return render_template('reset_requests.html',form=form,title="Reset Password")


#password_admin

@app.route("/password_admin",methods=["GET","POST"])
def password_admin():
    if current_user.username == 'admin':
        
        form = ResetForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")        
            current_user.password = hashed_password
            db.session.commit()
            flash(f'Your Password Has been updated !', 'success')
            return redirect(url_for('home_admin'))

        return render_template('reset_token.html',form=form,title="Reset Password")


@app.route("/reset_password/<token>",methods=["GET","POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid token or expired | انتهى التوكن ","warning")
        return redirect(url_for("reset_requests"))
    form = ResetForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")        
        user.password = hashed_password
        db.session.commit()
        flash(f'Your Password Has been updated !', 'success')
        return redirect(url_for('login'))

    return render_template('reset_token.html',form=form,title="Reset Password")

@app.route("/logout")
@login_required# we need to login
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    logout_user()
    return redirect(url_for('login'))



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _ , f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static','img',picture_fn) 

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required# we need to login
def account():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = UpdateAccountForm()
    image_file = url_for("static",filename="img/"+ current_user.image_file)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.ip_active_proxies = form.ip_active_proxies.data

        db.session.commit()
        flash("Successed Update Account - IP ",'success')
        return redirect(url_for('account'))
    elif request.method =="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email 
        form.ip_active_proxies.data = current_user.ip_active_proxies
    return render_template('account.html'
    ,title='Account Edit'
    ,image_file=image_file
    ,form=form)



