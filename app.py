from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default="Apartment")
    target = db.Column(db.Float, default=5000.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100))
    # Types: 'apartment' (adds to goal), 'expense' (general spending)
    ttype = db.Column(db.String(20)) 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not Goal.query.first():
        db.session.add(Goal(name="Apartment", target=5000.0))
        db.session.commit()

@app.route('/')
def index():
    user_goal = Goal.query.first()
    history = Transaction.query.order_by(Transaction.date_created.desc()).all()
    
    # MATH CHANGE: Only sum items where ttype is 'apartment'
    apartment_savings = sum(t.amount for t in history if t.ttype == 'apartment')
    
    # Sum general expenses separately just for display
    total_expenses = sum(t.amount for t in history if t.ttype == 'expense')
    
    percent = (apartment_savings / user_goal.target) * 100 if user_goal.target > 0 else 0
    return render_template('index.html', 
                           goal=user_goal, 
                           apartment_savings=apartment_savings, 
                           total_expenses=total_expenses,
                           percent=min(percent, 100), 
                           history=history)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    amount = float(request.form.get('amount'))
    source = request.form.get('source')
    ttype = request.form.get('type')
    new_tx = Transaction(amount=amount, source=source, ttype=ttype)
    db.session.add(new_tx)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    db.session.delete(Transaction.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_goal', methods=['POST'])
def update_goal():
    user_goal = Goal.query.first()
    user_goal.name = request.form.get('goal_name')
    user_goal.target = float(request.form.get('goal_target'))
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5003)