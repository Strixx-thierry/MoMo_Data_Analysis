import xml.etree.ElementTree as ET
import re
from datetime import datetime

tree= ET.parse("modified_sms_v2.xml")

root = tree.getroot()

sms_elements = root.findall("sms")

incoming_money=[]
payments=[]
transfers=[]
bank_deposits = []
airtime_bill = []
cash_power_bill = []
third_party_transactions = []
withdrawals = []
bank_transfer = []
bundle_purchase = []
incomplete_messages=[]
others=[]
def categorize_messages():
    for child in root:
        
        body_raw = child.get("body","")
        # lowercased and stripped version of body for matching
        
        body= body_raw.lower().strip()
        date = child.get("date", "")
        address = child.get("address", "")
        # msg = f"From: {child.get('address')}  \nDate:  {child.get('date')} \nMessage: {child.get('body')}"
        
        # To catch any incomplete messages with no body or address or date, maybe add other conditions
        if not body or not date or not address:
            incomplete_messages.append(child)
            continue
        
        
        if "you have received" in body:
            incoming_money.append(child)
        elif "payment" in body and 'completed' in body and 'airtime' not in body and 'cash power' not in body: 
            payments.append(child)
        elif "transfer" in body:
            transfers.append(child)
        elif "bank deposit" in body:
            bank_deposits.append(child)
        elif "airtime" in body:
            airtime_bill.append(child)
        elif "cash power" in body:
            cash_power_bill.append(child)
        elif "ltd" in body: #Try to add more keywords
            third_party_transactions.append(child)
        elif "withdrawn" in body:
            withdrawals.append(child)
        elif any(word in body for word in ['bundle', 'internet','data','voice']):
            bundle_purchase.append(child)
        else:
            others.append(child)
categorize_messages()


# Task 2- Data cleaning
# received- from, amount, date, message from sender, transaction id

incoming_money_cleaned = []

count = 0
for msg in incoming_money:
    count +=1
    incoming_money_dict={}
    body = msg.get("body","")
    
    #First key which is type= recieved for all
    incoming_money_dict["type"]="received"
    
    #matching the other keywords in the body
    # add else
    match_sender=re.search(r"from(.*?)\(",body)
    if match_sender:
       incoming_money_dict["sender"] = match_sender.group(1) 
       
    match_amount = re.search(r"received (\d+)",body)
    if match_amount:
       incoming_money_dict["amount"] = int(match_amount.group(1) )
    
    incoming_money_dict["body"]= body
    #Extract timestamp
    incoming_money_dict["timestamp"] = msg.get("readable_date","")
    
    # Extract message from sender
    
    match_sender_msg = re.search(r"Message from sender: (.*?)\. Your new balance", body)
    
    if match_sender_msg:
        incoming_money_dict["message_from_sender"]=match_sender_msg.group(1)
    
    
    # Extract transaction id
    
    match_txn_id = re.search(r"Financial Transcation Id: (\d+)",body)
    if match_txn_id:
        incoming_money_dict["transcation_id"] = match_txn_id.group(1)
    #
    
    
    #Append the dictionary to the list
    incoming_money_cleaned.append(incoming_money_dict)

print(incoming_money_cleaned)

print(count)

for msg in incoming_money_cleaned:
    print(msg)
