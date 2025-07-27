# ServQuick to QuickBooks Payment Importer

A Streamlit web app for finance teams to upload ServQuick payment CSVs and import them as Sales Receipts into QuickBooks Online, mapped by payment method.

## Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd qb_payment_importer
```

### 2. (Recommended) Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables
- Copy `.env.example` to `.env` and fill in your QuickBooks API credentials and company ID.

### 5. Run the Streamlit app
```bash
streamlit run app.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

---

## Notes
- Authenticate with QuickBooks Online via the sidebar before importing.
- Make sure your QuickBooks company has the referenced deposit accounts and a "Sales of Product Income" account.
- The app supports only CSV files with the required columns.

---

## License
MIT
