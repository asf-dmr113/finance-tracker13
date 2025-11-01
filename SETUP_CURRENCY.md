# Currency Converter Setup Guide

## ✅ What's Been Added

Your finance tracker now supports multiple currencies with automatic conversion to IDR:

### Supported Currencies
- **IDR** - Indonesian Rupiah (base currency)
- **USD** - US Dollar
- **JPY** - Japanese Yen
- **SGD** - Singapore Dollar
- **HKD** - Hong Kong Dollar
- **MYR** - Malaysian Ringgit
- **THB** - Thai Baht

### Features
- ✅ Real-time exchange rate fetching (uses exchangerate-api.com free tier)
- ✅ Automatic conversion to IDR before storing transactions
- ✅ Live conversion preview in the form
- ✅ Historical rates support (uses transaction date)
- ✅ Original currency and exchange rate stored with each transaction

## 📋 Setup Steps

### Step 1: Run Database Migration

You need to update your database to add the new currency fields. Choose one option:

**Option A: Add Columns (Recommended - Preserves existing data)**
```bash
python migrate_database.py
# Choose option 2
```

**Option B: Drop and Recreate (Development only - Deletes all data)**
```bash
python migrate_database.py
# Choose option 1
# ⚠️ WARNING: This will delete all existing transactions!
```

### Step 2: Test Currency Conversion

Test that the exchange rate API is working:

```bash
python test_currency_conversion.py
```

You should see successful conversions for all currencies.

### Step 3: Run Your Application

```bash
python app.py
```

The currency converter will automatically:
- Fetch current exchange rates when adding transactions
- Convert amounts to IDR before storing
- Show conversion preview in the form
- Display original currency info in transaction history

## 🎯 How to Use

1. **Adding a Transaction:**
   - Select the currency from the dropdown (defaults to IDR)
   - Enter the amount
   - The system will show a live preview: "≈ Rp X (Rate: 1 CURRENCY = Rp Y)"
   - The amount is automatically converted to IDR when saved

2. **Viewing Transactions:**
   - All amounts display in IDR
   - Original currency and exchange rate shown in transaction details
   - Example: "(1,000 JPY @ 107.96)"

3. **Historical Transactions:**
   - If you enter a past date, the system uses that day's exchange rate
   - Ensures accurate conversion based on transaction date

## 🔧 Troubleshooting

### Exchange Rate API Not Working

If you get errors fetching exchange rates:

1. **Check Internet Connection:**
   - The app needs internet to fetch exchange rates
   - Make sure you're connected to the internet

2. **API Limits:**
   - The free tier has rate limits
   - If you hit limits, wait a few minutes and try again

3. **Fallback API:**
   - The system automatically tries a fallback API if the primary fails
   - If both fail, check your internet connection

### Database Migration Issues

If migration fails:

1. **Make sure PostgreSQL is running:**
   ```bash
   # Check if postgres service is running
   ```

2. **Backup your data first:**
   - Use Option 2 (Add Columns) to preserve data
   - Only use Option 1 if you don't mind losing data

3. **Manual Migration:**
   - You can manually run SQL to add columns:
   ```sql
   ALTER TABLE transaction ADD COLUMN original_currency VARCHAR(3) DEFAULT 'IDR';
   ALTER TABLE transaction ADD COLUMN original_amount FLOAT;
   ALTER TABLE transaction ADD COLUMN exchange_rate FLOAT;
   ```

## 📝 Notes

- Exchange rates are fetched in real-time when you add a transaction
- Rates are cached per request (no duplicate API calls)
- Historical rates use the transaction date you specify
- All stored amounts are in IDR for consistent reporting

## 🚀 You're Ready!

After running the migration, your currency converter is ready to use!

