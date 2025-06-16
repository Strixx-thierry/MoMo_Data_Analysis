import os
import json
from data_cleaning.sms_loader import SMSLoader
from data_cleaning.categorizer import SMSCategorizer
from data_cleaning.cleaner import SMSCleaner
from database.db_manager import DBManager



def main():
    sms_file = "data_cleaning/modified_sms_v2.xml"
    loader= SMSLoader(sms_file)
    sms_elements = loader.load_sms()

    categorizer = SMSCategorizer()
    categorizer.categorize_messages(sms_elements)
    categories = categorizer.get_categories()

   
    for category, messages in categories.items():
        print(f"{category}: {len(messages)}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.abspath(os.path.join(script_dir, ".."))
    sample_outputs_dir = os.path.join(backend_dir, "sample_outputs")
    os.makedirs(sample_outputs_dir, exist_ok=True)

    output_dir = os.path.join(sample_outputs_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    for category, messages in categories.items():
        filename = os.path.join(output_dir, f"{category}.txt")
        with open(filename, "w") as f:
            for sms in messages:
                f.write(str(sms.attrib) + "\n")

    
    cleaner = SMSCleaner(categories)
    cleaner.clean_all()

    cleaned_dir = os.path.join(sample_outputs_dir, "cleaned_output")
    os.makedirs(cleaned_dir, exist_ok=True)
    from collections import defaultdict
    cleaned_by_type = defaultdict(list)
    for item in cleaner.cleaned_data:
        t = item.get("type", "unknown")
        cleaned_by_type[t].append(item)
    for t, items in cleaned_by_type.items():
        filename = os.path.join(cleaned_dir, f"{t}.txt")
        with open(filename, "w") as f:
            for entry in items:
                f.write(str(entry) + "\n")
     
     
                
    # Insert cleaned data into the database
    db = DBManager()
    
    required_keys = [
    'transaction_id', 'type', 'timestamp', 'amount', 'status', 'sender', 'recipient',
    'recipient_phone', 'agent_name', 'agent_phone', 'fee', 'bundle_type',
    'message_from_sender', 'body'] 
    for item in cleaner.cleaned_data:
        for key in required_keys:
                if key not in item:
                    item[key] = None
        db.insert_transactions(item)
    db.close()
    
    
    # Export cleaned data to JSON
    
    with open('cleaned_sms_data.json', 'w') as f:
        json.dump(cleaner.cleaned_data, f, indent=2)
    
    print("\nProcessing complete! Check the following files:")
    print("- transactions.db (SQLite database)")
    print("- cleaned_sms_data.json (JSON export)")
    print("- unprocessed.log (Unprocessed messages)")
    

if __name__ == "__main__":
    main()