from quickbooks.objects.salesreceipt import SalesReceipt, SalesReceiptLine, PaymentMethodRef, DepositToAccountRef
from quickbooks.objects.base import Ref
from quickbooks.objects.customer import Customer
from quickbooks.objects.detailline import SalesItemLine
from quickbooks.objects.item import Item
from quickbooks.objects.account import Account
import datetime

# Hardcoded mapping: Payment type to QuickBooks DepositToAccount name
PAYMENT_TYPE_TO_ACCOUNT = {
    "Cash": "Cash on hand",
    "Card": "Bank Account",
    "Credit": "Accounts Receivable",
    "Bkash": "Bkash Account",
    "E-Gen": "E-Gen Account"
}

# Helper: Find account by name
def get_account_ref_by_name(qb_client, name):
    accounts = Account.filter(Name=name, qb=qb_client)
    if accounts:
        return Ref(accounts[0].Id, "Account")
    else:
        raise Exception(f"Account '{name}' not found in QuickBooks.")

# Helper: Find or create a generic customer
def get_or_create_generic_customer(qb_client, location_name):
    customers = Customer.filter(DisplayName=location_name, qb=qb_client)
    if customers:
        return customers[0]
    # Create if not exists
    customer = Customer()
    customer.DisplayName = location_name
    customer.save(qb=qb_client)
    return customer

# Helper: Find or create a generic item
def get_or_create_generic_item(qb_client):
    items = Item.filter(Name="ServQuick Sale", qb=qb_client)
    if items:
        return items[0]
    # Create if not exists
    item = Item()
    item.Name = "ServQuick Sale"
    item.Type = "Service"
    item.IncomeAccountRef = get_account_ref_by_name(qb_client, "Sales of Product Income")
    item.save(qb=qb_client)
    return item

def import_sales_receipts(df, qb_client):
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

            # Build sales receipt line
            line = SalesItemLine()
            line.Amount = float(row["Payment Amount"])
            line.ItemRef = Ref(item.Id, "Item")
            line.Qty = 1
            # Optionally add tax as a separate line or field

            sales_receipt = SalesReceipt()
            sales_receipt.CustomerRef = Ref(customer.Id, "Customer")
            sales_receipt.TxnDate = datetime.datetime.strptime(str(row["Sales Date"]), "%Y-%m-%d").date()
            sales_receipt.Line = [line]
            sales_receipt.DepositToAccountRef = deposit_account_ref
            sales_receipt.PrivateNote = f"Imported from ServQuick: {payment_type}"
            sales_receipt.save(qb=qb_client)
            logs.append(f"Row {idx+1}: Imported successfully as SalesReceipt #{sales_receipt.Id}.")
        except Exception as e:
            logs.append(f"Row {idx+1}: Failed to import. Error: {e}")
    return logs
