from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

toDoListApp = Flask(__name__, template_folder="C:\Users\Dell\Desktop\to-do-list\templates\index.html")
toDoListApp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
toDoListApp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
toDoListApp.config['SECRET_KEY'] = 'your_secret_key'

toDoListApp.static_folder = 'css'

db = SQLAlchemy(toDoListApp)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.name}>"


with toDoListApp.app_context():
    db.create_all()


@toDoListApp.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    all_completed = len(tasks) > 0 and all(task.is_completed for task in tasks)
    return render_template('index.html', tasks=tasks, all_completed=all_completed, )


@toDoListApp.route('/add', methods=['POST'])
def add_task():
    task_name = request.form['task']

    if task_name:
        new_task = Task(name=task_name)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))


@toDoListApp.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('index'))


@toDoListApp.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    toDoListApp.run(debug=True)
