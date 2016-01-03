from datetime import date
import uuid
from flask import Flask, url_for, abort
from flask import request, session, flash, redirect, render_template
from py2neo import Graph, Node, Relationship
import time


app = Flask(__name__)
# app.config['_Response_uri'] = '/home/okech/Downloads/neo4j-community-2.3.1/data/graph.db'

# authenticate("localhost:7474", "neo4j", " neo4j")
graph = Graph("http://localhost:7474/db/data/")

user = Node("User", username="Juliet")
report = Node("Report", title="Accident at voi",
               road="nairobi-nakuru", details="a saloon car rammed into a PSV bus")
tag = Node("Tag", name="arusha")


class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        else:
            return False

    def add_report(self, title, road, details):
        user = self.find()
        report = Node(
            "Report",
            id=str(uuid.uuid4()),
            title=title,
            road=road,details=details,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, "REPORTED", report)
        graph.create(rel)



class Report:
    def __init__(self, title):
        self.title = title

    def find(self):
        report = graph.find_one("Report", "title", self.title)
        return report

    def enter_report(self, when, road, details):
        if not self.find():
            report = Node("Report", title=self.title, when=time.ctime(when), road=road, details=details)
            graph.create(Report)
            return True
        else:
            return False

graph.create(Relationship(user, "REPORTED", report))
graph.create(Relationship(tag, "TAGGED", report))


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            error = 'Username must be at least one characters'
        elif len(password) < 5:
            error = 'Password must be at least five characters'
        elif not User(username).register(password):
            error = 'A user with that username already exists'
        else:
            session['username'] = username
            flash('Logged in')
            return redirect(url_for('index'))
    return render_template('register.html', error=error)


@app.route('/add_report', methods=['POST'])
def add_report():
    title = request.form('title')
    road = request.form('road')
    details = request.form('details')

    if not title:
        abort(400, 'you must enter the report title')
    if not road:
        abort(400, 'you must enter the accident road')
    if not details:
        abort(400, 'you must enter the accident details')

    User(session['username']).add_title(title, road, details)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run()
