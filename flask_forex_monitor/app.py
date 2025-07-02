import json
import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, redirect, render_template, url_for, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret-key')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Usuários em memória
USERS = {
    'admin': 'secret'
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

ALERT_FILE = os.path.join(os.path.dirname(__file__), 'alerts.json')


def load_alerts():
    if not os.path.exists(ALERT_FILE):
        return []
    with open(ALERT_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_alert(alert):
    alerts = load_alerts()
    alerts.append(alert)
    with open(ALERT_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)


def send_email(subject, body):
    user = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    to_email = os.environ.get('TO_EMAIL')
    if not (user and password and to_email):
        print('Gmail credentials not configured.')
        return
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())
    except Exception as e:
        print('Failed to send email:', e)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Credenciais inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    alerts = load_alerts()
    return render_template('index.html', alerts=alerts)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json or {}
    alert = {
        'symbol': data.get('symbol'),
        'message': data.get('message')
    }
    save_alert(alert)
    send_email(f"Alerta: {alert['symbol']}", alert['message'])
    return {'status': 'ok'}


@app.route('/')
def index():
    """Redirect users to the appropriate page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
