from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
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
    amount = db.Column(db.Float, nullable=False)  # Stored in IDR
    transaction_type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50))
    original_currency = db.Column(db.String(3), default='IDR')  # Store original currency code
    original_amount = db.Column(db.Float)  # Store original amount before conversion
    exchange_rate = db.Column(db.Float)  # Store the exchange rate used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'date': self.date.isoformat(),
            'category': self.category or '',
            'original_currency': self.original_currency or 'IDR',
            'original_amount': self.original_amount,
            'exchange_rate': self.exchange_rate,
            'created_at': self.created_at.isoformat()
        }

# Currency Conversion Functions
def get_exchange_rate(from_currency, to_currency='IDR', date=None):
    """
    Get exchange rate from a free API
    Uses exchangerate-api.com (free tier, no API key required)
    For historical dates, uses alternative free API if primary fails
    """
    # Check if date is today or in the future - use latest rates
    from datetime import date as date_class
    today = date_class.today()
    
    if date and date > today:
        # Future dates - use latest rate
        date = None
    
    try:
        # Primary API: exchangerate-api.com v4 (free, no API key needed)
        if date:
            # Try historical endpoint first
            url = f'https://api.exchangerate-api.com/v4/historical/{from_currency}/{date.strftime("%Y-%m-%d")}'
        else:
            # Latest rates
            url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
        
        response = requests.get(url, timeout=10)
        
        # If historical endpoint returns 404, fall back to latest rates
        if response.status_code == 404 and date:
            print(f"Historical rate not available for {date}, using latest rate instead")
            url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
            response = requests.get(url, timeout=10)
        
        response.raise_for_status()
        data = response.json()
        
        # exchangerate-api.com v4 response format
        if 'rates' in data:
            if to_currency in data['rates']:
                return float(data['rates'][to_currency])
            else:
                raise ValueError(f"Currency {to_currency} not found in API response")
        else:
            raise ValueError(f"Invalid API response format")
    
    except requests.RequestException as e:
        # Fallback: Try using exchangerate.host (old endpoint without key requirement)
        try:
            if date:
                # For historical, try the date endpoint
                url = f'https://api.exchangerate.host/{date.strftime("%Y-%m-%d")}'
                params = {
                    'base': from_currency,
                    'symbols': to_currency
                }
            else:
                url = 'https://api.exchangerate.host/latest'
                params = {
                    'base': from_currency,
                    'symbols': to_currency
                }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # exchangerate.host format
            if data.get('success') is True and 'rates' in data:
                if to_currency in data['rates']:
                    return float(data['rates'][to_currency])
            
            # If still failing, use latest rate for historical dates
            if date:
                print(f"Using latest exchange rate instead of historical rate for {date}")
                # Use latest rate directly without recursion
                url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if 'rates' in data and to_currency in data['rates']:
                    return float(data['rates'][to_currency])
                raise ValueError(f"Currency {to_currency} not found")
            else:
                raise ValueError(f"Fallback API failed: {data.get('error', 'Unknown error')}")
        except Exception as fallback_error:
            # Last resort: if it's a historical date and all APIs fail, use latest rate
            if date:
                print(f"Warning: Could not fetch historical rate for {date}, using latest rate")
                try:
                    # Get latest rate directly
                    url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if 'rates' in data and to_currency in data['rates']:
                        return float(data['rates'][to_currency])
                    raise ValueError(f"Currency {to_currency} not found")
                except Exception as final_error:
                    raise ValueError(f"Could not fetch exchange rate for {from_currency} to {to_currency}. Please check your internet connection: {str(final_error)}")
            else:
                print(f"Fallback API also failed: {fallback_error}")
                raise ValueError(f"Could not fetch exchange rate for {from_currency} to {to_currency}. Please check your internet connection.")
    
    except Exception as e:
        print(f"Error processing exchange rate: {e}")
        # Last resort for historical dates: return latest rate
        if date:
            print(f"Using latest exchange rate instead of historical rate for {date}")
            try:
                # Get latest rate directly
                url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                if 'rates' in data and to_currency in data['rates']:
                    return float(data['rates'][to_currency])
                raise ValueError(f"Currency {to_currency} not found")
            except Exception as final_error:
                raise ValueError(f"Could not fetch exchange rate for {from_currency} to {to_currency}: {str(final_error)}")
        raise ValueError(f"Could not fetch exchange rate for {from_currency} to {to_currency}: {str(e)}")

def convert_to_idr(amount, from_currency, transaction_date=None):
    """Convert amount from given currency to IDR"""
    if from_currency == 'IDR':
        return amount, 1.0
    
    try:
        # Use the transaction date for historical rates, or today's date
        rate = get_exchange_rate(from_currency, 'IDR', transaction_date)
        converted_amount = amount * rate
        return converted_amount, rate
    except Exception as e:
        print(f"Conversion error: {e}")
        # Return a reasonable fallback or raise
        raise ValueError(f"Failed to convert {amount} {from_currency} to IDR: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/exchange-rate', methods=['GET'])
def get_exchange_rate_api():
    """API endpoint to get current exchange rate"""
    from_currency = request.args.get('from', 'USD')
    to_currency = request.args.get('to', 'IDR')
    date_str = request.args.get('date')
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        rate = get_exchange_rate(from_currency, to_currency, date)
        return jsonify({
            'success': True,
            'from': from_currency,
            'to': to_currency,
            'rate': rate,
            'date': date_str or datetime.now().date().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    
    # Get currency info
    original_currency = data.get('currency', 'IDR').upper()
    original_amount = float(data['amount'])
    
    # Convert to IDR if not already IDR
    transaction_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    if original_currency == 'IDR':
        converted_amount = original_amount
        exchange_rate = 1.0
    else:
        try:
            converted_amount, exchange_rate = convert_to_idr(original_amount, original_currency, transaction_date)
        except Exception as e:
            return jsonify({
                'error': f'Currency conversion failed: {str(e)}'
            }), 400
    
    transaction = Transaction(
        description=data['description'],
        amount=converted_amount,  # Store in IDR
        transaction_type=data['transaction_type'],
        date=transaction_date,
        category=data.get('category', ''),
        original_currency=original_currency,
        original_amount=original_amount,
        exchange_rate=exchange_rate
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

