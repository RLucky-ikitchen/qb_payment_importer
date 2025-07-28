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
                st.experimental_rerun()
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
    required_cols = [
        "Location name", "Sales date", "Payment name", "Payment type", "Payment amount", "Tender tax amount"
    ]
    missing = [col for col in required_cols if col not in df.columns]
    return missing

if uploaded_file:
    try:
        # Read CSV skipping first 2 rows and using 3rd row as header
        df = pd.read_csv(uploaded_file, skiprows=2, header=0)
        
        # Clean up the data - remove summary rows and empty rows
        df = df.dropna(subset=['Payment amount'])  # Remove rows with no payment amount
        df = df[df['Payment amount'] != 0]  # Remove rows with zero payment amount (optional)
        
        missing_cols = validate_columns(df)
        if missing_cols:
            st.error(f"Missing columns: {', '.join(missing_cols)}. Please upload a standardized file.")
        else:
            st.success("File uploaded and validated!")
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
else:
    st.info("Please upload a ServQuick payment CSV file to begin.")

# --- Footer ---
st.markdown("---")
st.caption("Developed for Finance Team | ServQuick → QuickBooks Online Importer")
