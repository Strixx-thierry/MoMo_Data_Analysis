const express = require('express');
const cors = require('cors');
const multer = require('multer');
const xml2js = require('xml2js');
const { Pool } = require('pg');
const path = require('path');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Database configuration
const pool = new Pool({
    connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost/momo_db'
});

// Configure multer for file upload
const upload = multer({ dest: 'uploads/' });

// Helper functions
function parseAmount(text) {
    const match = text.match(/(\d+(?:\.\d+)?)\s*RWF/);
    return match ? parseFloat(match[1]) : 0;
}

function parseTransactionId(text) {
    const match = text.match(/Transaction ID:\s*(\d+)/);
    return match ? match[1] : null;
}

function categorizeTransaction(text) {
    text = text.toLowerCase();
    if (text.includes('you have received')) return 'incoming_money';
    if (text.includes('payment') && text.includes('completed') && !text.includes('airtime') && !text.includes('cash power')) return 'payment';
    if (text.includes('transfer')) return 'transfer';
    if (text.includes('bank deposit')) return 'bank_deposit';
    if (text.includes('airtime')) return 'airtime';
    if (text.includes('cash power')) return 'cash_power';
    if (text.includes('ltd')) return 'third_party';
    if (text.includes('withdrawn')) return 'withdrawal';
    if (['bundle', 'internet', 'data', 'voice'].some(word => text.includes(word))) return 'bundle';
    return 'other';
}

// Create database table if it doesn't exist
async function initializeDatabase() {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                transaction_type VARCHAR(50),
                amount DECIMAL,
                sender VARCHAR(255),
                recipient VARCHAR(255),
                transaction_id VARCHAR(255) UNIQUE,
                timestamp TIMESTAMP,
                message TEXT,
                fee DECIMAL,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('Database initialized successfully');
    } catch (error) {
        console.error('Error initializing database:', error);
    }
}

// Initialize database
initializeDatabase();

// Routes
app.post('/upload', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        const parser = new xml2js.Parser();
        const xmlData = await parser.parseStringPromise(req.file.buffer);
        const transactions = [];

        for (const sms of xmlData.sms_data.sms) {
            const body = sms.body[0];
            if (!body) continue;

            const transaction = {
                transaction_type: categorizeTransaction(body),
                amount: parseAmount(body),
                transaction_id: parseTransactionId(body),
                message: body,
                timestamp: new Date(),
                status: 'completed'
            };

            transactions.push(transaction);
        }

        // Insert transactions into database
        for (const transaction of transactions) {
            await pool.query(
                `INSERT INTO transactions 
                (transaction_type, amount, transaction_id, message, timestamp, status)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (transaction_id) DO NOTHING`,
                [
                    transaction.transaction_type,
                    transaction.amount,
                    transaction.transaction_id,
                    transaction.message,
                    transaction.timestamp,
                    transaction.status
                ]
            );
        }

        res.json({ message: `Successfully processed ${transactions.length} transactions` });
    } catch (error) {
        console.error('Error processing file:', error);
        res.status(500).json({ error: 'Error processing file' });
    }
});

app.get('/transactions', async (req, res) => {
    try {
        const { skip = 0, limit = 100, type } = req.query;
        let query = 'SELECT * FROM transactions';
        const params = [];

        if (type) {
            query += ' WHERE transaction_type = $1';
            params.push(type);
        }

        query += ' ORDER BY timestamp DESC LIMIT $' + (params.length + 1) + ' OFFSET $' + (params.length + 2);
        params.push(parseInt(limit), parseInt(skip));

        const result = await pool.query(query, params);
        res.json(result.rows);
    } catch (error) {
        console.error('Error fetching transactions:', error);
        res.status(500).json({ error: 'Error fetching transactions' });
    }
});

app.get('/statistics', async (req, res) => {
    try {
        const totalTransactions = await pool.query('SELECT COUNT(*) FROM transactions');
        const totalAmount = await pool.query('SELECT SUM(amount) FROM transactions');
        
        const typeStats = await pool.query(`
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as amount
            FROM transactions
            GROUP BY transaction_type
        `);

        res.json({
            total_transactions: parseInt(totalTransactions.rows[0].count),
            total_amount: parseFloat(totalAmount.rows[0].sum) || 0,
            type_statistics: typeStats.rows.map(row => ({
                type: row.transaction_type,
                count: parseInt(row.count),
                amount: parseFloat(row.amount) || 0
            }))
        });
    } catch (error) {
        console.error('Error fetching statistics:', error);
        res.status(500).json({ error: 'Error fetching statistics' });
    }
});

// Start server
app.listen(port, () => {
    console.log(`Server running on port ${port}`);
}); 