from flask import Flask, render_template, request, redirect, url_for
import sqlite3 as sql
import hash_passwords

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'


@app.route('/')
def login_start():
    return render_template('login.html')


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # realpython.com/introduction-to-flask-part-2-creating-a-login-page/
    error = None

    # get email and password from form
    email = request.form['email']
    password = request.form['password']

    # hash the password to compare to database
    password = hash_passwords.hash_password(password)

    # check if given email and hashed password exist in database
    connection = sql.connect('users.db')
    cursor = connection.execute('SELECT * FROM users WHERE email=? AND password=?;', (email, password))
    user = cursor.fetchone()

    # invalid credentials
    if user is None:
        error = 'Login failed: User not found in database'
        return render_template('login.html', error=error)

    # Valid credentials
    else:
        print("login success!")
        return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.debug = True
    app.run()
