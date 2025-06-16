import sqlite3

class DBManager:
    def __init__(self, db_file="transactions.db"):
    # connect to database file
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
        
    def create_tables(self):
        # Read schema file and execute
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        self.conn.executescript(schema)
        
    def insert_transactions(self, data):
        try:
            with self.conn:
                self.conn.execute('''INSERT INTO transactions (transaction_id, type, timestamp, body, amount, status, sender, recipient, recipient_phone, agent_name, agent_phone, fee, bundle_type, message_from_sender) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    data.get('transaction_id'),
                    data.get('type'),
                    data.get('timestamp'),
                    data.get('body'),  
                    data.get('amount'),
                    data.get('status'), 
                    data.get('sender'),
                    data.get('recipient'),
                    data.get('recipient_phone'),
                    data.get('agent_name'),
                    data.get('agent_phone'),
                    data.get('fee'),
                    data.get('bundle_type'),
                    data.get('message_from_sender'),
                    
                    ))
                return True
        except sqlite3.IntegrityError:
            # handle duplicate entries
            print(f"Duplicate entry for transaction_id: {data.get('transaction_id')}")
            return False
    def close(self):
        self.conn.close()
            
    