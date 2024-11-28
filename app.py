import cv2
import os
import bcrypt
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user, UserMixin, LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Email, Length
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

# Set up the secret key and SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SentinelCam'

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

# initialize csrf
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    """Model for user accounts."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    # One-to-many relationship: A user can have multiple image logs
    image_logs = db.relationship('ImageLog', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class ImageLog(db.Model):
    """Model for storing image logs."""
    __tablename__ = 'imagelog'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to the User model
    filename = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp when the image is captured

    def __repr__(self):
        return f'<ImageLog {self.filename} for User {self.user_id}>'


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "John Doe"})
    email = EmailField(validators=[InputRequired(), Length(min=8, max=30)], render_kw={"placeholder": "Johndoe@yahoo.co"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=30)], render_kw={"placeholder": "password"})
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder": "johndoe@yahoo.co"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=30)], render_kw={"placeholder": "password"})
    submit = SubmitField("Login")


def capture_image():
    cam = cv2.VideoCapture(0)  # 0 is the default camera
    if not cam.isOpened():
        print("Failed to access the camera")
        return None

    # Ensure the directory exists
    os.makedirs('static/images', exist_ok=True)

    result, image = cam.read()
    if result:
        # Define the filename
        filename = f"static/images/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        # Save the image
        cv2.imwrite(filename, image)
        print(f"Image saved as {filename}")
        cam.release()  # Release the camera
        return filename  # Return the path of the saved image
    else:
        print("Failed to capture image")
        cam.release()  # Release the camera
        return None


def send_email(image_path, receiver_email):
    if image_path is None:
        print("No image to send")
        return  # No image to send

    sender_email = "laptopsecureme@gmail.com"
    password = "ywlv dmrh cjxk ures"  # Use app-specific password or environment variable

    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Laptop Access Detected"

    # Attach the file
    with open(image_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(image_path)}")
        msg.attach(part)

    # Sending the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Use port 587 for TLS
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent with attachment {os.path.basename(image_path)}")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/capture', methods=['GET', 'POST'])
@login_required
def capture_and_send_email():
    image_path = capture_image()

    if image_path:
        send_email(image_path, current_user.email)

        new_log = ImageLog(user_id=current_user.id, filename=image_path)
        try:
            db.session.add(new_log)
            db.session.commit()
            flash("Image captured and sent successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to save image log: {e}", "error")

        now = datetime.now()
        session['last_sent_date'] = now.strftime('%Y-%m-%d')
        session['last_sent_time'] = now.strftime('%H:%M:%S')

    else:
        flash("Failed to capture image", "error")

    return redirect(url_for('dashboard'))


@app.route('/userdata')
@login_required
def user_data():
    image_logs = ImageLog.query.filter_by(user_id=current_user.id).all()
    return render_template('user_data.html', image_logs=image_logs)

@app.route('/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    # Fetch the log to be deleted
    log_to_delete = ImageLog.query.filter_by(id=log_id, user_id=current_user.id).first()
    
    if log_to_delete:
        try:
            # Remove the file from the file system
            if os.path.exists(log_to_delete.filename):
                os.remove(log_to_delete.filename)

            # Delete the log from the database
            db.session.delete(log_to_delete)
            db.session.commit()
            flash("Log deleted successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while deleting the log: {e}", "danger")
    else:
        flash("Log not found or access denied.", "danger")

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    image_logs = ImageLog.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', image_logs=image_logs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Check your credentials.", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:
            flash("Email or Username taken.", "danger")
            return render_template('register.html', form=form)
        else:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Registration successful!", "success")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "danger")
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!", "success")
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
