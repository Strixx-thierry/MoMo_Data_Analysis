import re

class SMSCleaner:
    def __init__(self, categories):
        self.categories= categories
        self.cleaned_data = []
    
    def log_unprocessed_messages(self):
        """
        Log unproccessed or ignored messages to a separate file
        in a readable format
        """
        with open('unprocessed.log', 'w') as f:
            f.write("Unprocessed SMS Messages Log\n")
            f.write('----------------------------\n')
            for sms in self.categories['unprocessed']:
                f.write(f"Body: {sms.get('body', 'N/A')}\n")
                f.write(f"Date: {sms.get('readable_date', 'N/A')}\n")
                f.write(f"Address: {sms.get('address', 'N/A')}\n")
                f.write('----------------------------\n')
    
    def extract_common_attributes(self,msg, transaction_type): 
        '''
        Extract common attributes from all categories
        ''' 
        body = msg.get('body','')
        
        data = {"type": transaction_type,"body": body,"timestamp": msg.get("readable_date",""),"address": msg.get("address", ""),"raw_date": msg.get("date", "")}
        # Extract transaction ID
        tid_patterns = [r"transaction id: \s*(\w+)",r"txid: \s*(\w+)"]
        
        for pattern in tid_patterns:
            tid_match = re.search(pattern, body, re.IGNORECASE)
            if tid_match:
                data["transaction_id"] = tid_match.group(1)
                break
        # Extract status
        if re.search(r"\bfailed\b", body, re.IGNORECASE):
            data["status"] = "failed"
        else:
            data["status"] = "completed"
            
        return data    
    def clean_incoming_money(self):
        '''
        Clean messages under the incoming money category
        '''  
        for msg in self.categories['incoming_money']:
            data = self.extract_common_attributes(msg, "incoming_money")
            body = msg.get("body", "")
        
         # Extract sender
            sender_match = re.search(r"from\s+([^.]+?)(?:\s*\(|\.|$)", body, re.IGNORECASE)
            if sender_match:
                data["sender"] = sender_match.group(1).strip()
            
            # Extract amount
            amount_match = re.search(r"received\s+(\d+)\s*rwf", body, re.IGNORECASE)
            if amount_match:
                data["amount"] = int(amount_match.group(1))
            
            # Extract message from sender
            msg_match = re.search(r"message from sender:\s*([^.]+)", body, re.IGNORECASE)
            if msg_match:
                data["message_from_sender"] = msg_match.group(1).strip()
            
            self.cleaned_data.append(data)      
    
    def clean_payments(self):
        '''
        Clean and structure messages for payments to code holders
        '''  
        for msg in self.categories['payments']:
            data = self.extract_common_attributes(msg, "payment")
            body = msg.get("body", "")
        
            recipient_match = re.search(r"to\s+([A-Za-z\s]+?)\s+\d+", body)
            if recipient_match:
                data["recipient"] = recipient_match.group(1).strip()
            
            # Extract amount
            amount_match = re.search(r"payment of\s*([\d,]+)\s*RWF", body)
            if amount_match:
                data["amount"] = int(amount_match.group(1).replace(",", ""))
    
            
            self.cleaned_data.append(data)
            
    def clean_withdrawals(self):
        '''
        Clean and structure messages for withdrawals from agents
        '''
        for msg in self.categories['withdrawals']:
            data = self.extract_common_attributes(msg, "withdrawal")
            body = msg.get("body", "")
            
            # Extract agent information
            agent_match = re.search(r"agent:\s*([^(]+)\s*\(([^)]+)\)", body, re.IGNORECASE)
            if agent_match:
                data["agent_name"] = agent_match.group(1).strip()
                data["agent_phone"] = agent_match.group(2).strip()
            # Extract amount
            amount_match = re.search(r"withdrawn\s+(\d+)\s*rwf", body, re.IGNORECASE)
            if amount_match:
                data["amount"] = int(amount_match.group(1))
            
            self.cleaned_data.append(data)
            
    def clean_bundle_purchases(self):
        ''' Clean and strucutre data for bundle purchases
        '''
        for msg in self.categories['bundle_purchase']:
            data = self.extract_common_attributes(msg, "bundle_purchase")
            body = msg.get("body", "")
            
            # Extract bundle type
            bundle_match = re.search(r"purchased.*?bundle of\s+(\d+(?:\.\d+)?)\s*([a-z]+)", body, re.IGNORECASE)
            if bundle_match:
                data["bundle_type"] = bundle_match.group(1).strip()
            
            # Extract amount
            amount_match = re.search(r"for\s+(\d+)\s*rwf", body, re.IGNORECASE)
            if amount_match:
                data["amount"] = int(amount_match.group(1))
            
            self.cleaned_data.append(data)
    def clean_airtime_bills(self):
        ''' Clean and structure messages for airtime bills
        '''
        for msg in self.categories['airtime_bill']:
            data = self.extract_common_attributes(msg, "airtime_bill")
            body = msg.get("body", "")
            
            # Extract amount
            amount_match = re.search(r"payment of\s+(\d+)\s*rwf.*?airtime", body, re.IGNORECASE)
            if amount_match:
                data["amount"] = int(amount_match.group(1))
            
            
            
            # Extract fee
            fee_match = re.search(r"fee:\s*(\d+)\s*rwf", body, re.IGNORECASE)
            if fee_match:
                data["fee"] = int(fee_match.group(1))
                
                
            self.cleaned_data.append(data)
            
    def clean_transfers(self):
        '''
        Clean and strucure messages for both bank and mobile transfers
        '''
        for msg in self.categories['transfers']:
            data = self.extract_common_attributes(msg, 'transfers')
            body = msg.get("body", "")
            match = re.search(r"\*165\*S\*(\d+)\s*RWF transferred to\s+(.+?)\s*\((2507\d{7,8})\).*?fee was:\s*(\d+)\s*rwf",body, re.IGNORECASE)
            if match:
                    data['amount'] = int(match.group(1))
                    data['recipient_name'] = match.group(2).strip()
                    data['recipient_phone'] = match.group(3).strip()
                    data['fee'] = int(match.group(4))
            self.cleaned_data.append(data)  
              
    def clean_bank_transfers(self):
        
        for msg in self.categories['bank_transfer']:
            data = self.extract_common_attributes(msg, "bank_transfer")
            body = msg.get("body", "")
            
            match = re.search(r"You have transferred\s+(\d+)\s*RWF to\s+(.+?)\s*\((2507\d{6,8})\)", body,re.IGNORECASE)# Extract amount
            if match:
                data["amount"] = int(match.group(1))
                data["recipient_name"] = match.group(2).strip()
                data["recipient_phone"] = match.group(3).strip()
                
            self.cleaned_data.append(data)
    def clean_all(self):
        self.log_unprocessed_messages()
        self.clean_incoming_money()
        self.clean_payments()
        self.clean_withdrawals()
        self.clean_bundle_purchases()
        self.clean_airtime_bills()
        self.clean_transfers()
        self.clean_bank_transfers()
        
        # Basic cleaning for the other categories
        for category in ['bank_deposits', 'cash_power_bill', 
                        'third_party_transactions']:
            for msg in self.categories[category]:
                data = self.extract_common_attributes(msg, category)
                # Extract amount for all categories
                amount_match = re.search(r"(\d+)\s*rwf", msg.get("body", ""), re.IGNORECASE)
                if amount_match:
                    data["amount"] = int(amount_match.group(1))
                self.cleaned_data.append(data)  
                