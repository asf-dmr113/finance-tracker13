from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from config import config

app = Flask(__name__)

# Configuration - using PostgreSQL
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

db = SQLAlchemy(app)

# Database Models
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'date': self.date.isoformat(),
            'category': self.category or '',
            'created_at': self.created_at.isoformat()
        }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    transaction = Transaction(
        description=data['description'],
        amount=float(data['amount']),
        transaction_type=data['transaction_type'],
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        category=data.get('category', '')
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify(transaction.to_dict()), 201

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'}), 200

@app.route('/api/summary', methods=['GET'])
def get_summary():
    transactions = Transaction.query.all()
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expense = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    balance = total_income - total_expense
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    })

# Initialize database
def init_db():
    with app.app_context():
        try:
            # Test connection first
            db.engine.connect()
            print("✓ Database connection successful!")
            db.create_all()
            print("✓ Database tables created/verified successfully!")
        except Exception as e:
            error_msg = str(e)
            print("\n" + "="*60)
            print("DATABASE CONNECTION ERROR")
            print("="*60)
            print(f"Error: {error_msg}")
            print("\nTroubleshooting steps:")
            print("1. Verify PostgreSQL is running:")
            print("   - Windows: Check Services (services.msc) for 'postgresql'")
            print("   - Or check Task Manager for postgres processes")
            print("\n2. Verify your PostgreSQL credentials:")
            print(f"   Current connection string: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("\n3. To set custom credentials, use environment variable:")
            print("   PowerShell: $env:DATABASE_URL='postgresql://user:password@localhost:5432/dbname'")
            print("   Or create a .env file with: DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
            print("\n4. To reset postgres user password:")
            print("   - Open psql: psql -U postgres")
            print("   - Run: ALTER USER postgres WITH PASSWORD 'your_new_password';")
            print("   - Update your connection string accordingly")
            print("\n5. Create the database if it doesn't exist:")
            print("   psql -U postgres -c 'CREATE DATABASE personalfinancetracker;'")
            print("="*60 + "\n")
            raise

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)

