from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# This points to finance.db in your main folder, NOT the instance folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'finance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False) 
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100))

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Apartment Deposit")
    target = db.Column(db.Float, default=1000.0)

# Create tables automatically
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    transactions = Transaction.query.all()
    goal_data = Goal.query.first()
    
    if not goal_data:
        goal_data = Goal(name="Apartment Deposit", target=1000.0)
        db.session.add(goal_data)
        db.session.commit()

    current_savings = sum(t.amount for t in transactions if t.transaction_type == 'Goal')
    
    progress = 0
    if goal_data.target > 0:
        progress = min((current_savings / goal_data.target) * 100, 100)
    
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
    
    new_t = Transaction(transaction_type=t_type, amount=amount, description=description)
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
    t = db.session.get(Transaction, id)
    if t:
        db.session.delete(t)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)