import datetime
from quickbooks.objects.salesreceipt import SalesReceipt
from quickbooks.objects.customer import Customer
from quickbooks.objects.item import Item
from quickbooks.objects.account import Account
from quickbooks.exceptions import QuickbooksException

# Hardcoded mapping: Payment name to QuickBooks DepositToAccount name
PAYMENT_NAME_TO_ACCOUNT = {
    "Cash": "Cash on hand",
    "Card": "Bank Account",
    "Bkash": "Bkash Account",
    "E-Gen": "E-Gen Account",
    "Due Bill": "Accounts Receivable"
}

def get_account_ref_by_name(qb_client, name):
    """Get QuickBooks account reference by name"""
    try:
        # Search for account by name
        accounts = Account.filter(qb_client, DisplayName=name)
        if accounts:
            return accounts[0].to_ref()
        else:
            # If account doesn't exist, create it
            account = Account()
            account.Name = name
            account.AccountType = "Bank"  # Default to Bank account type
            account.save(qb_client)
            return account.to_ref()
    except QuickbooksException as e:
        print(f"Error getting account {name}: {e}")
        return None

def get_or_create_generic_customer(qb_client, location_name):
    """Get or create a customer in QuickBooks"""
    try:
        # Search for existing customer
        customers = Customer.filter(qb_client, DisplayName=location_name)
        if customers:
            return customers[0]
        else:
            # Create new customer
            customer = Customer()
            customer.DisplayName = location_name
            customer.save(qb_client)
            return customer
    except QuickbooksException as e:
        print(f"Error creating customer {location_name}: {e}")
        return None

def get_or_create_generic_item(qb_client):
    """Get or create a generic service item for ServQuick sales"""
    try:
        # Search for existing item
        items = Item.filter(qb_client, Name="ServQuick Sale")
        if items:
            return items[0]
        else:
            # Create new item
            item = Item()
            item.Name = "ServQuick Sale"
            item.Type = "Service"
            item.Description = "Service sale imported from ServQuick"
            item.save(qb_client)
            return item
    except QuickbooksException as e:
        print(f"Error creating item: {e}")
        return None

def import_sales_receipts(df, qb_client):
    """
    Import sales receipts to QuickBooks Online using real API calls.
    """
    logs = []
    item = get_or_create_generic_item(qb_client)
    
    if not item:
        logs.append("ERROR: Could not create or find generic item. Import aborted.")
        return logs
    
    for idx, row in df.iterrows():
        try:
            # Map payment name to deposit account
            payment_name = row["Payment name"]
            deposit_account_name = PAYMENT_NAME_TO_ACCOUNT.get(payment_name)
            if not deposit_account_name:
                logs.append(f"Row {idx+1}: Unknown payment name '{payment_name}'. Skipped.")
                continue
            
            deposit_account_ref = get_account_ref_by_name(qb_client, deposit_account_name)
            if not deposit_account_ref:
                logs.append(f"Row {idx+1}: Could not find/create deposit account '{deposit_account_name}'. Skipped.")
                continue

            # Find or create customer using Payment name as customer name
            customer = get_or_create_generic_customer(qb_client, row["Payment name"])
            if not customer:
                logs.append(f"Row {idx+1}: Could not create customer '{row['Payment name']}'. Skipped.")
                continue

            # Create sales receipt
            sales_receipt = SalesReceipt()
            sales_receipt.CustomerRef = customer.to_ref()
            sales_receipt.TxnDate = datetime.datetime.strptime(str(row["Sales date"]), "%Y-%m-%d").date()
            sales_receipt.DepositToAccountRef = deposit_account_ref
            sales_receipt.PrivateNote = f"Imported from ServQuick: {payment_name}"
            
            # Add line item
            from quickbooks.objects.detailline import SalesItemLineDetail
            from quickbooks.objects.line import Line
            
            line = Line()
            line.Amount = float(row["Payment amount"])
            line.DetailType = "SalesItemLineDetail"
            
            line_detail = SalesItemLineDetail()
            line_detail.ItemRef = item.to_ref()
            line_detail.Qty = 1
            line_detail.UnitPrice = float(row["Payment amount"])
            
            line.SalesItemLineDetail = line_detail
            sales_receipt.Line = [line]
            
            # Save to QuickBooks
            sales_receipt.save(qb_client)
            logs.append(f"Row {idx+1}: Imported successfully as SalesReceipt #{sales_receipt.Id}.")
            
        except QuickbooksException as e:
            logs.append(f"Row {idx+1}: QuickBooks API error: {e}")
        except Exception as e:
            logs.append(f"Row {idx+1}: Failed to import. Error: {e}")
    
    return logs
