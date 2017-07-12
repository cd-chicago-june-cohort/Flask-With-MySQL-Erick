from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app, 'email')
app.secret_key = ('98256db73640b8dd4a3b9096665ec4ed')

@app.route('/')
def main():

    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if len(request.form['email']) < 1:
        flash("Please enter a email!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Please enter a valid email!")
        return redirect('/')
    else:
        session['newEmail'] = request.form['email']
        query = 'insert into email(email, created_at)value(:Email, NOW())'
        email = {
            'Email' : request.form['email']
        }
        mysql.query_db(query, email)
        return redirect('/success')

@app.route('/success')
def success():
    query = 'select * from email'
    emailsFromQuery = mysql.query_db(query)
    return render_template('success.html', email = emailsFromQuery, newEmail = session['newEmail'])

app.run(debug = True)