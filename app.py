from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
import hash_passwords

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


def validate(email, password):
    # check if given email and hashed password exist in database
    connection = sql.connect('users.db')
    cursor = connection.execute('SELECT * FROM users WHERE email=? AND password=?;', (email, password))
    user = cursor.fetchone()

    if user is None:
        error = 'Login failed: User not found in database'
        return False

    return True


@app.route('/login', methods=['POST'])
def login():
    error = None
    # get email and password from form
    email = request.form['email']
    password = request.form['password']

    if not email or not password:
        login_success = 0
        return render_template('login.html', login_success=login_success)

    # hash the password to compare to database
    password = hash_passwords.hash_password(password)

    if not validate(email, password):
        # TODO add thing that says login failed
        # TODO clear input fields
        login_success = 0
        return render_template('login.html', login_success=login_success)

    else:
        login_success = 1
        return render_template("homepage.html", login_success=login_success)


if __name__ == '__main__':
    app.debug = True
    app.run()
