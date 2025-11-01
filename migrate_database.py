"""
Database Migration Script
Adds currency conversion fields to Transaction model

WARNING: Option 1 will DELETE ALL existing transactions!
Only use Option 1 if you're in development and can lose data.
"""
from app import app, db, Transaction

def migrate_option1_drop_recreate():
    """Option 1: Drop and recreate tables (DANGER: Deletes all data!)"""
    print("\n" + "="*60)
    print("WARNING: This will DELETE ALL existing transactions!")
    print("="*60)
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return False
    
    with app.app_context():
        try:
            print("\nDropping all tables...")
            db.drop_all()
            print("Creating new tables...")
            db.create_all()
            print("\n✓ Database migration completed!")
            print("All tables have been recreated with new currency fields.")
            return True
        except Exception as e:
            print(f"\n✗ Error during migration: {e}")
            return False

def migrate_option2_add_columns():
    """Option 2: Add new columns to existing table (preserves data)"""
    with app.app_context():
        try:
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('transaction')]
            
            print("\n" + "="*60)
            print("Adding currency conversion columns...")
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
                print("✓ All currency columns already exist!")
                return True
            
            # Add columns using raw SQL
            with db.engine.connect() as conn:
                for col_name, col_type in columns_to_add:
                    print(f"Adding column: {col_name}...")
                    try:
                        # For PostgreSQL
                        if 'postgresql' in str(db.engine.url):
                            conn.execute(text(f'ALTER TABLE transaction ADD COLUMN {col_name} {col_type}'))
                        # For SQLite
                        elif 'sqlite' in str(db.engine.url):
                            # SQLite doesn't support ALTER TABLE ADD COLUMN easily
                            print(f"⚠ SQLite detected. Consider using Flask-Migrate for better SQLite support.")
                            conn.execute(text(f'ALTER TABLE transaction ADD COLUMN {col_name} {col_type}'))
                        else:
                            conn.execute(text(f'ALTER TABLE transaction ADD COLUMN {col_name} {col_type}'))
                        conn.commit()
                        print(f"✓ Added column: {col_name}")
                    except Exception as e:
                        if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                            print(f"  Column {col_name} already exists, skipping...")
                        else:
                            print(f"  Warning: {e}")
                
                # Update existing records to have default values
                print("\nUpdating existing records...")
                update_sql = text("""
                    UPDATE transaction 
                    SET original_currency = COALESCE(original_currency, 'IDR'),
                        original_amount = COALESCE(original_amount, amount),
                        exchange_rate = COALESCE(exchange_rate, 1.0)
                    WHERE original_currency IS NULL OR original_amount IS NULL OR exchange_rate IS NULL
                """)
                result = conn.execute(update_sql)
                conn.commit()
                print(f"✓ Updated {result.rowcount} existing records")
            
            print("\n✓ Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n✗ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Database Migration Tool")
    print("="*60)
    print("\nChoose migration option:")
    print("1. Drop and recreate tables (DANGER: Deletes all data)")
    print("2. Add columns to existing table (Preserves data)")
    print("3. Cancel")
    
    choice = input("\nEnter your choice (1/2/3): ")
    
    if choice == '1':
        migrate_option1_drop_recreate()
    elif choice == '2':
        migrate_option2_add_columns()
    elif choice == '3':
        print("Migration cancelled.")
    else:
        print("Invalid choice.")

