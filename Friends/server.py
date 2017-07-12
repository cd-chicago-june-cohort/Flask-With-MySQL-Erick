from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app, 'friends')

@app.route('/')
def main():
    query = 'select * from friend'
    newFriend = mysql.query_db(query)
    return render_template('index.html', friend = newFriend)

@app.route('/addFriend', methods = ['POST'])
def addFriend():

    query = 'insert into friend (name, age, friend_since)values(:name, :age, NOW())'
    info = {
        'name' : request.form['name'],
        'age' : request.form['age'] 
    }
    mysql.query_db(query, info)

    return redirect('/')
app.run(debug = True)
