# PostgreSQL Database Setup

This project uses PostgreSQL instead of SQLite. Follow these steps to set up your database:

## Prerequisites

1. **Install PostgreSQL** on your system:
   - Windows: Download from [PostgreSQL official website](https://www.postgresql.org/download/windows/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql` (Ubuntu/Debian)

2. **Start PostgreSQL service**:
   - Windows: PostgreSQL should start automatically as a service
   - macOS: `brew services start postgresql`
   - Linux: `sudo systemctl start postgresql`

## Database Setup

### Option 1: Using psql (PostgreSQL command line)

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database
CREATE DATABASE personalfinancetracker;

# (Optional) Create a dedicated user
CREATE USER tracker_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE personalfinancetracker TO tracker_user;

# Exit psql
\q
```

### Option 2: Using pgAdmin

1. Open pgAdmin
2. Right-click on "Databases" → Create → Database
3. Name it `personalfinancetracker`
4. Click Save

## Configuration

### Default Connection String

The default connection string is:
```
postgresql://postgres:postgres@localhost:5432/personalfinancetracker
```

### Custom Configuration via Environment Variable

You can override the database connection by setting the `DATABASE_URL` environment variable:

**Windows PowerShell:**
```powershell
$env:DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

**Windows CMD:**
```cmd
set DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

**Linux/macOS:**
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

Or create a `.env` file in the project root:
```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

The database tables will be created automatically when you first run the application.

## Troubleshooting

### Connection Error

If you get a connection error:
1. Make sure PostgreSQL is running
2. Check your username, password, and database name
3. Verify PostgreSQL is listening on port 5432 (default port)
4. Check firewall settings if connecting remotely

### Authentication Failed

- Verify your PostgreSQL user password
- Check `pg_hba.conf` for authentication settings
- Try resetting the postgres user password

### Database Does Not Exist

- Create the database first using the steps above
- Make sure you're connecting to the correct database name

