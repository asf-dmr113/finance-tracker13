"""
Test PostgreSQL connection script
Run this to diagnose database connection issues
"""
import os
import sys

def test_connection():
    """Test PostgreSQL connection with helpful error messages"""
    print("Testing PostgreSQL Connection...")
    print("=" * 60)
    
    # Get connection string from environment or use default
    database_url = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/personalfinancetracker'
    
    print(f"Connection string: {database_url.replace(database_url.split('@')[0].split(':')[-1], '***') if '@' in database_url else database_url}")
    print()
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the connection string
        parsed = urlparse(database_url)
        
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:] if parsed.path else 'None'}")
        print(f"User: {parsed.username}")
        print()
        
        # Test connection
        print("Attempting to connect...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:] if parsed.path else 'postgres',
            user=parsed.username,
            password=parsed.password
        )
        
        print("[SUCCESS] Connection successful!")
        
        # Check if database exists
        cur = conn.cursor()
        db_name = parsed.path[1:] if parsed.path else None
        if db_name:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if exists:
                print(f"[SUCCESS] Database '{db_name}' exists")
            else:
                print(f"[ERROR] Database '{db_name}' does NOT exist")
                print(f"\n  To create it, run:")
                print(f"  psql -U {parsed.username} -c 'CREATE DATABASE {db_name};'")
        
        cur.close()
        conn.close()
        print("\n[SUCCESS] All checks passed! Your database connection is working.")
        return True
        
    except ImportError:
        print("[ERROR] psycopg2 is not installed")
        print("  Install it with: pip install psycopg2-binary")
        return False
    except psycopg2.OperationalError as e:
        error_str = str(e)
        print("[ERROR] Connection failed!")
        print(f"\nError: {error_str}\n")
        
        if "password authentication failed" in error_str.lower():
            print("SOLUTION: Password authentication failed")
            print("This means your PostgreSQL password doesn't match.")
            print("\nOptions:")
            print("1. Set the correct password via environment variable:")
            print("   PowerShell: $env:DATABASE_URL='postgresql://postgres:YOUR_PASSWORD@localhost:5432/personalfinancetracker'")
            print("\n2. Reset the postgres user password:")
            print("   a. Open Windows Command Prompt or PowerShell")
            print("   b. Run: psql -U postgres")
            print("   c. Enter your current postgres password (if prompted)")
            print("   d. Run: ALTER USER postgres WITH PASSWORD 'newpassword';")
            print("   e. Update your DATABASE_URL accordingly")
        elif "could not connect" in error_str.lower() or "connection refused" in error_str.lower():
            print("SOLUTION: PostgreSQL service is not running")
            print("1. Check if PostgreSQL is running:")
            print("   - Open Services (Win+R, type 'services.msc')")
            print("   - Look for 'postgresql' service")
            print("   - If stopped, right-click and select 'Start'")
            print("\n2. Or check Task Manager for 'postgres' processes")
        elif "does not exist" in error_str.lower():
            db_name = parsed.path[1:] if parsed.path else 'personalfinancetracker'
            print(f"SOLUTION: Database '{db_name}' does not exist")
            print(f"\nCreate it with:")
            print(f"  psql -U {parsed.username} -c 'CREATE DATABASE {db_name};'")
        
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

