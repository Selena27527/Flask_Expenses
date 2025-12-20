from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Updated to use finance.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'Goal' or 'Expense'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Apartment Deposit")
    target = db.Column(db.Float, default=1000.0)

# IMPORTANT: This creates the database tables on Render automatically
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    transactions = Transaction.query.all()
    goal_data = Goal.query.first()
    if not goal_data:
        goal_data = Goal(name="Apartment Deposit", target=1000.0)
        db.session.add(goal_data)
        db.session.commit()

    current_savings = sum(t.amount for t in transactions if t.type == 'Goal')
    progress = min((current_savings / goal_data.target) * 100, 100) if goal_data.target > 0 else 0
    
    return render_template('index.html', 
                           transactions=transactions, 
                           current_savings=current_savings, 
                           goal=goal_data, 
                           progress=round(progress, 1))

@app.route('/add', methods=['POST'])
def add_transaction():
    t_type = request.form.get('type')
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    
    new_t = Transaction(type=t_type, amount=amount, description=description)
    db.session.add(new_t)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_goal', methods=['POST'])
def update_goal():
    goal_data = Goal.query.first()
    if goal_data:
        goal_data.name = request.form.get('goal_name')
        goal_data.target = float(request.form.get('goal_target'))
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_transaction(id):
    t = Transaction.query.get(id)
    if t:
        db.session.delete(t)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)