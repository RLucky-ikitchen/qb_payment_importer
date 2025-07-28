import streamlit as st
import pandas as pd
from importer import import_sales_receipts  # Assume this function handles the import logic
from qb_auth import get_qb_auth_url, exchange_code_for_token, is_authenticated, get_qb_client  # Assume these handle auth
import os

st.set_page_config(page_title="ServQuick to QuickBooks Importer", layout="centered")
st.title("ServQuick Payment Importer for QuickBooks Online")

# --- Sidebar: QuickBooks Authentication ---
st.sidebar.header("QuickBooks Authentication")

if not is_authenticated():
    auth_url = get_qb_auth_url()
    st.sidebar.markdown(f"[Login to QuickBooks Online]({auth_url})")
    code = st.sidebar.text_input("Paste the authorization code here:")
    if st.sidebar.button("Authenticate"):
        if code:
            success = exchange_code_for_token(code)
            if success:
                st.sidebar.success("Authenticated with QuickBooks!")
                st.rerun()
            else:
                st.sidebar.error("Authentication failed. Check the code and try again.")
        else:
            st.sidebar.warning("Please enter the authorization code.")
else:
    st.sidebar.success("Authenticated with QuickBooks!")

# --- Main UI: CSV Upload and Preview ---
st.header("Step 1: Upload ServQuick Payment CSV")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])  # Only CSV for now

def validate_columns(df):
    # Clean column names by stripping whitespace
    df.columns = df.columns.str.strip()
    
    required_cols = [
        "Location name", "Sales date", "Payment name", "Payment type", "Payment amount", "Tender tax amount"
    ]
    missing = [col for col in required_cols if col not in df.columns]
    return missing, df.columns.tolist()

if uploaded_file:
    try:
        # Read CSV skipping first 1 row and using 2nd row as header
        st.info("Reading CSV file...")
        df = pd.read_csv(uploaded_file, skiprows=1, header=0)
        st.success(f"CSV loaded successfully. Found {len(df)} rows.")
        
        # Show raw column names for debugging
        st.write("Raw column names:", df.columns.tolist())
        
        # Validate columns first
        missing_cols, actual_cols = validate_columns(df)
        if missing_cols:
            st.error(f"Missing columns: {', '.join(missing_cols)}")
            st.error(f"Actual columns found: {', '.join(actual_cols)}")
            st.error("Please upload a standardized ServQuick export file.")
        else:
            st.success("Columns validated successfully!")
            
            # Clean up the data - remove summary rows and empty rows
            st.info("Cleaning data...")
            initial_rows = len(df)
            
            # Check if Payment amount column exists before cleaning
            if 'Payment amount' in df.columns:
                df = df.dropna(subset=['Payment amount'])  # Remove rows with no payment amount
                df = df[df['Payment amount'] != 0]  # Remove rows with zero payment amount (optional)
                final_rows = len(df)
                st.success(f"Data cleaned: {initial_rows} → {final_rows} rows")
            else:
                st.error("Payment amount column not found after validation!")
                st.stop()
            
            st.subheader("Preview Data")
            st.dataframe(df.head(20))
            st.write(f"Total rows: {len(df)}")

            # --- Step 2: Import to QuickBooks ---
            st.header("Step 2: Import to QuickBooks Online")
            if not is_authenticated():
                st.warning("Please authenticate with QuickBooks in the sidebar before importing.")
            else:
                if st.button("Import to QuickBooks"):
                    with st.spinner("Importing sales receipts to QuickBooks..."):
                        # Call the import logic (stubbed)
                        try:
                            qb_client = get_qb_client()
                            logs = import_sales_receipts(df, qb_client)
                            st.success("Import completed!")
                            st.subheader("Import Log")
                            for log in logs:
                                st.write(log)
                        except Exception as e:
                            st.error(f"Import failed: {e}")
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.error("Please ensure the CSV file is a valid ServQuick export with the correct format.")
        # Show more debug info
        st.write("Debug info:")
        st.write(f"File name: {uploaded_file.name}")
        st.write(f"File size: {uploaded_file.size} bytes")
else:
    st.info("Please upload a ServQuick payment CSV file to begin.")

# --- Footer ---
st.markdown("---")
st.caption("Developed for Finance Team | ServQuick → QuickBooks Online Importer")
