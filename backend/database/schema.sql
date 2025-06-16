CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE,
    type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    body TEXT,
    amount INTEGER,
    status TEXT,
    sender TEXT,
    recipient TEXT,
    recipient_phone TEXT,
    agent_name TEXT,
    agent_phone TEXT,
    fee INTEGER,
    bundle_type TEXT,
    message_from_sender TEXT
);
