import re

class SMSCategorizer:
    def __init__(self):
        self.categories = {
            "incoming_money": [],
            "payments": [],
            "transfers": [],
            "bank_deposits": [],
            "airtime_bill": [],
            "cash_power_bill": [],
            "third_party_transactions": [],
            "withdrawals": [],
            "bank_transfer": [],
            "bundle_purchase": [],
            "unprocessed": [],
        
        }
    def categorize_messages(self, sms_elements):
        '''
        Categorize messages based on their content and patterns
        and store each message in a list
        '''
        for sms in sms_elements:
            body_raw = sms.get("body", "")
            
            # Lowercased and stripped version of body for matching
            body = body_raw.lower().strip()
            date = sms.get("date", "")
            address = sms.get("address", "")
            
            # Catch any incomplete messages with no body or address or date
            if not body or not date or not address:
                self.categories['unprocessed'].append(sms)
                continue
            
            # Logic for categorization
            
            if "you have received" in body and "rwf" in body:
                self.categories["incoming_money"].append(sms)
            elif "bank deposit" in body:
                self.categories["bank_deposits"].append(sms)  
            elif any(word in body for word in ["ltd", "wasac"]) or re.search(r'\b(?:[A-Z]{3,}\s){1,3}[A-Z]{3,}\b', body_raw):
                self.categories["third_party_transactions"].append(sms)
            elif (("transfer" in body and 'bank' not in body) or ('payment' in body and re.search(r'\(2507\d{8}\)', body_raw))):
                self.categories["transfers"].append(sms)
            elif "payment" in body and 'completed' in body and 'airtime' not in body and 'cash power' not in body and 'bundles' not in body and 'ltd' not in body:
                self.categories["payments"].append(sms)
            
            
            elif "airtime" in body:
                self.categories["airtime_bill"].append(sms)
            elif "cash power" in body:
                self.categories["cash_power_bill"].append(sms)
            elif "withdrawn" in body:
                self.categories["withdrawals"].append(sms)
            elif "bank transfer" in body or ("transfer" in body and "bank" in body):
                self.categories["bank_transfer"].append(sms)
            elif any(word in body for word in ['bundle', 'bundles', 'packs', 'internet', 'data', 'voice']):
                self.categories["bundle_purchase"].append(sms)
            else:
                self.categories["unprocessed"].append(sms)
    def get_categories(self):
        return self.categories