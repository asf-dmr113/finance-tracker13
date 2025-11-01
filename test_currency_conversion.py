"""
Test Currency Conversion
Tests the exchange rate API and conversion functionality
"""
from app import app
from app import get_exchange_rate, convert_to_idr
from datetime import datetime

def test_exchange_rates():
    """Test fetching exchange rates for all supported currencies"""
    print("\n" + "="*60)
    print("Testing Exchange Rate API")
    print("="*60)
    
    currencies = ['USD', 'JPY', 'SGD', 'HKD', 'MYR', 'THB']
    
    with app.app_context():
        for currency in currencies:
            try:
                rate = get_exchange_rate(currency, 'IDR')
                print(f"[SUCCESS] {currency} -> IDR: 1 {currency} = Rp {rate:,.2f}")
            except Exception as e:
                print(f"[ERROR] {currency} -> IDR: Error - {e}")
    
    print("\n" + "="*60)
    print("Testing Currency Conversion")
    print("="*60)
    
    # Test conversions
    test_cases = [
        ('USD', 100),
        ('JPY', 10000),
        ('SGD', 50),
        ('HKD', 200),
        ('MYR', 100),
        ('THB', 1000),
    ]
    
    with app.app_context():
        for currency, amount in test_cases:
            try:
                converted, rate = convert_to_idr(amount, currency)
                print(f"[SUCCESS] {amount} {currency} = Rp {converted:,.0f} (Rate: {rate:.4f})")
            except Exception as e:
                print(f"[ERROR] {amount} {currency}: Error - {e}")

def test_historical_rates():
    """Test fetching historical exchange rates"""
    print("\n" + "="*60)
    print("Testing Historical Exchange Rates")
    print("="*60)
    
    # Test with a date from last week
    from datetime import datetime, timedelta
    test_date = datetime.now().date() - timedelta(days=7)
    
    with app.app_context():
        try:
            rate = get_exchange_rate('USD', 'IDR', test_date)
            print(f"[SUCCESS] Historical rate (USD -> IDR on {test_date}): {rate:,.2f}")
        except Exception as e:
            print(f"[ERROR] Historical rate test failed: {e}")

if __name__ == '__main__':
    test_exchange_rates()
    test_historical_rates()
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

