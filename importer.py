import datetime

# Mock implementation - replace with actual QuickBooks SDK calls
class MockRef:
    def __init__(self, id, type):
        self.Id = id
        self.type = type

class MockSalesReceipt:
    def __init__(self):
        self.Id = None
        self.CustomerRef = None
        self.TxnDate = None
        self.Line = []
        self.DepositToAccountRef = None
        self.PrivateNote = None
    
    def save(self, qb):
        # Mock save - in real implementation, this would call QuickBooks API
        self.Id = f"mock_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return self

# Hardcoded mapping: Payment type to QuickBooks DepositToAccount name
PAYMENT_TYPE_TO_ACCOUNT = {
    "Cash": "Cash on hand",
    "Card": "Bank Account",
    "Credit": "Accounts Receivable",
    "Bkash": "Bkash Account",
    "E-Gen": "E-Gen Account"
}

def get_account_ref_by_name(qb_client, name):
    # Mock implementation - replace with actual QuickBooks SDK call
    return MockRef(f"account_{name.replace(' ', '_')}", "Account")

def get_or_create_generic_customer(qb_client, location_name):
    # Mock implementation - replace with actual QuickBooks SDK call
    class MockCustomer:
        def __init__(self, name):
            self.Id = f"customer_{name.replace(' ', '_')}"
            self.DisplayName = name
    return MockCustomer(location_name)

def get_or_create_generic_item(qb_client):
    # Mock implementation - replace with actual QuickBooks SDK call
    class MockItem:
        def __init__(self):
            self.Id = "item_servquick_sale"
            self.Name = "ServQuick Sale"
            self.Type = "Service"
    return MockItem()

def import_sales_receipts(df, qb_client):
    """
    Mock implementation of sales receipt import.
    Replace the mock classes and methods with actual QuickBooks SDK calls.
    """
    logs = []
    item = get_or_create_generic_item(qb_client)
    
    for idx, row in df.iterrows():
        try:
            # Map payment type to deposit account
            payment_type = row["Payment type"]
            deposit_account_name = PAYMENT_TYPE_TO_ACCOUNT.get(payment_type)
            if not deposit_account_name:
                logs.append(f"Row {idx+1}: Unknown payment type '{payment_type}'. Skipped.")
                continue
            deposit_account_ref = get_account_ref_by_name(qb_client, deposit_account_name)

            # Find or create customer
            customer = get_or_create_generic_customer(qb_client, row["Location name"])

            # Create sales receipt
            sales_receipt = MockSalesReceipt()
            sales_receipt.CustomerRef = MockRef(customer.Id, "Customer")
            sales_receipt.TxnDate = datetime.datetime.strptime(str(row["Sales Date"]), "%Y-%m-%d").date()
            sales_receipt.DepositToAccountRef = deposit_account_ref
            sales_receipt.PrivateNote = f"Imported from ServQuick: {payment_type}"
            
            # Mock save
            sales_receipt.save(qb_client)
            logs.append(f"Row {idx+1}: Imported successfully as SalesReceipt #{sales_receipt.Id}.")
            
        except Exception as e:
            logs.append(f"Row {idx+1}: Failed to import. Error: {e}")
    
    return logs
