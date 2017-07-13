from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'MyKeyBoi'

mysql = MySQLConnector(app, 'wall')

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/login', methods = ['POST'])
def login():
    errors = True
    if len(request.form['email']) < 1:
        flash('Please enter an email!')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Please enter a valid email!")
    elif len(request.form['password']) < 1:
        flash("Please enter the password!")
    else:
        errors = False
    if errors == True:
        return redirect('/')
    else:
        passwordHashed = md5.new(request.form['password']).hexdigest()
        query = 'select id, firstname, email, password from users where email = :Email and password = :password'
        user = {
            'Email' : request.form['email'],
            'password' : passwordHashed
        }
        checkDB = mysql.query_db(query, user)
    if (len(checkDB) != 1):
        flash('Please register before logging in!')
        return redirect('/')
    else:
        session['id'] = checkDB[0]['id']
        session['firstname'] = checkDB[0]['firstname']
        return redirect('/wall')
    
@app.route('/register', methods = ['POST'])
def register():
    errors = True
    if len(request.form['firstName']) == 0 or len(request.form['firstName']) < 2:
        flash('All fields are required')
    elif len(request.form['lastName']) == 0 or len(request.form['lastName']) < 2:
        flash('All fields are required')
    elif not EMAIL_REGEX.match(request.form['email']) or len(request.form['lastName']) < 1:
        flash('Please enter a valid email!')
    elif len(request.form['password']) < 8:
        flash('Password(s) must be longer than 8 characters!')
    elif request.form['password'] != request.form['confirmPassword']:
        flash('Passwords must match!')
    else:
        errors = False
    if errors == True:
        return redirect('/')
    else:
        passwordHashed = md5.new(request.form['password']).hexdigest()
        query = 'insert into users(firstname, lastname, email, password, created_at, updated_at)value(:firstName, :lastName, :email, :password, NOW(), NOW())'
        newUser = {
            'firstName' : request.form['firstName'],
            'lastName' : request.form['lastName'],
            'email' : request.form['email'],
            'password' : passwordHashed
        }
        mysql.query_db(query, newUser)
        flash('Successfully created account!')
        return redirect('/')

@app.route('/wall')
def wall():
    queryMessages = 'select concat(firstname, " ", lastname) as name, date_format(messages.created_at, "%b %D %Y") as date, message, messages.created_at, messages.id from messages join users on users_id=users.id order by created_at desc'
    messages = mysql.query_db(queryMessages)
    queryComments = 'select concat(firstname, " " ,lastname) as name, comments.created_at, comment, messages_id from users join comments on users.id = users_id'
    comments = mysql.query_db(queryComments)
    return render_template('wall.html', messagesFromQuery = messages, commentsFromQuery = comments)    

@app.route('/post', methods=['POST'])
def post():
    userID = session['id']
    message = request.form['message']
    query = 'insert into messages (users_id, message, created_at) value (:userID, :message, NOW())'
    info = {
        'userID' : userID,
        'message' : message
    }
    mysql.query_db(query, info)
    return redirect('/wall')

@app.route('/comment', methods=['POST'])
def comment():
    userID = session['id']
    comment = request.form['comment']
    messageID = request.form['messageID']
    query = 'insert into comments (messages_id, users_id, comment, created_at) value (:messageID, :userID, :comment, NOW())'
    info = {
        'messageID' : messageID,
        'userID' : userID,
        'comment' : comment
    }
    mysql.query_db(query, info)
    return redirect('/wall')

app.run(debug = True)