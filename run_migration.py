"""
Quick Migration Script - Automatically adds currency columns
This preserves all existing data
"""
from app import app, db
from sqlalchemy import inspect, text

def add_currency_columns():
    """Automatically add currency columns to existing table"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('transaction')]
            
            print("\n" + "="*60)
            print("Adding Currency Conversion Columns")
            print("="*60)
            
            # Check which columns need to be added
            columns_to_add = []
            if 'original_currency' not in columns:
                columns_to_add.append(("original_currency", "VARCHAR(3) DEFAULT 'IDR'"))
            if 'original_amount' not in columns:
                columns_to_add.append(("original_amount", "FLOAT"))
            if 'exchange_rate' not in columns:
                columns_to_add.append(("exchange_rate", "FLOAT"))
            
            if not columns_to_add:
                print("[SUCCESS] All currency columns already exist!")
                return True
            
            # Add columns using raw SQL
            with db.engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    print(f"Adding column: {col_name}...")
                    try:
                        # PostgreSQL syntax
                        if 'postgresql' in str(db.engine.url):
                            conn.execute(text(f'ALTER TABLE transaction ADD COLUMN IF NOT EXISTS {col_name} {col_type}'))
                        else:
                            # Generic SQL
                            conn.execute(text(f'ALTER TABLE transaction ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                        print(f"[SUCCESS] Added column: {col_name}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'already exists' in error_str or 'duplicate column' in error_str or 'duplicate' in error_str:
                            print(f"[INFO] Column {col_name} already exists, skipping...")
                        else:
                            print(f"[WARNING] Error adding {col_name}: {e}")
                            # Try without IF NOT EXISTS for databases that don't support it
                            try:
                                conn.execute(text(f'ALTER TABLE transaction ADD COLUMN {col_name} {col_type}'))
                                conn.commit()
                                print(f"[SUCCESS] Added column: {col_name} (retry succeeded)")
                            except Exception as e2:
                                print(f"[ERROR] Failed to add {col_name}: {e2}")
                                return False
                
                # Update existing records to have default values
                print("\nUpdating existing records...")
                try:
                    update_sql = text("""
                        UPDATE transaction 
                        SET original_currency = COALESCE(original_currency, 'IDR'),
                            original_amount = COALESCE(original_amount, amount),
                            exchange_rate = COALESCE(exchange_rate, 1.0)
                        WHERE original_currency IS NULL OR original_amount IS NULL OR exchange_rate IS NULL
                    """)
                    result = conn.execute(update_sql)
                    conn.commit()
                    print(f"[SUCCESS] Updated {result.rowcount} existing records")
                except Exception as e:
                    print(f"[WARNING] Could not update existing records: {e}")
                    # This is okay, new records will have the defaults
            
            print("\n[SUCCESS] Database migration completed!")
            print("You can now add transactions with currency conversion.")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Currency Conversion Database Migration")
    print("="*60)
    print("\nThis will add the following columns to your transaction table:")
    print("  - original_currency (stores the original currency code)")
    print("  - original_amount (stores the original amount)")
    print("  - exchange_rate (stores the exchange rate used)")
    print("\nExisting data will be preserved.")
    
    success = add_currency_columns()
    
    if success:
        print("\n" + "="*60)
        print("Migration Complete!")
        print("="*60)
        print("\nYour database is now ready for currency conversion.")
        print("Restart your Flask app to use the new features.")
    else:
        print("\n" + "="*60)
        print("Migration Failed!")
        print("="*60)
        print("\nPlease check the error messages above.")
        print("You may need to run the migration manually using migrate_database.py")

