from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

app = Flask(_name_)
CORS(app)  # Enable CORS for frontend integration

class DatabaseManager:
    def _init_(self, db_file="transactions.db"):
        self.db_file = db_file
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def dict_factory(self, cursor, row):
        """Convert SQLite row to dictionary"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filtering"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        conn.row_factory = db.dict_factory
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        transaction_type = request.args.get('type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        min_amount = request.args.get('min_amount')
        max_amount = request.args.get('max_amount')
        search = request.args.get('search')
        
        # Build query with filters
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)
        
        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to)
        
        if min_amount:
            query += " AND amount >= ?"
            params.append(int(min_amount))
        
        if max_amount:
            query += " AND amount <= ?"
            params.append(int(max_amount))
        
        if search:
            query += " AND (body LIKE ? OR sender LIKE ? OR recipient LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        conn.close()
        return jsonify({
            'status': 'success',
            'data': transactions,
            'count': len(transactions)
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction_details(transaction_id):
    """Get detailed information for a specific transaction"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        conn.row_factory = db.dict_factory
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        
        conn.close()
        
        if transaction:
            return jsonify({
                'status': 'success',
                'data': transaction
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Transaction not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get summary analytics for dashboard"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        conn.row_factory = db.dict_factory
        cursor = conn.cursor()
        
        # Total transactions by type
        cursor.execute("""
            SELECT type, COUNT(*) as count, 
                   COALESCE(SUM(amount), 0) as total_amount,
                   COALESCE(AVG(amount), 0) as avg_amount
            FROM transactions 
            WHERE amount IS NOT NULL 
            GROUP BY type
        """)
        by_type = cursor.fetchall()
        
        # Monthly transaction volume
        cursor.execute("""
            SELECT substr(timestamp, 1, 7) as month, 
                   COUNT(*) as count,
                   COALESCE(SUM(amount), 0) as total_amount
            FROM transactions 
            WHERE amount IS NOT NULL 
            GROUP BY substr(timestamp, 1, 7)
            ORDER BY month
        """)
        monthly_data = cursor.fetchall()
        
        # Transaction status distribution
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM transactions 
            GROUP BY status
        """)
        status_data = cursor.fetchall()
        
        # Top recipients/senders
        cursor.execute("""
            SELECT recipient, COUNT(*) as count, SUM(amount) as total_amount
            FROM transactions 
            WHERE recipient IS NOT NULL AND amount IS NOT NULL
            GROUP BY recipient
            ORDER BY total_amount DESC
            LIMIT 10
        """)
        top_recipients = cursor.fetchall()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                COALESCE(SUM(amount), 0) as total_volume,
                COALESCE(AVG(amount), 0) as average_amount,
                COALESCE(MAX(amount), 0) as max_amount,
                COALESCE(MIN(amount), 0) as min_amount
            FROM transactions 
            WHERE amount IS NOT NULL
        """)
        overall_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'by_type': by_type,
                'monthly': monthly_data,
                'by_status': status_data,
                'top_recipients': top_recipients,
                'overall': overall_stats
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/transaction-types', methods=['GET'])
def get_transaction_types():
    """Get all available transaction types"""
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT type FROM transactions WHERE type IS NOT NULL ORDER BY type")
        types = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            'status': 'success',
            'data': types
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if _name_ == '_main_':
    print("Starting SMS Transaction Dashboard API...")
    print("API will be available at: http://localhost:5000")
    print("Available endpoints:")
    print("- GET /api/transactions - Get all transactions with filtering")
    print("- GET /api/transactions/<id> - Get specific transaction details")
    print("- GET /api/analytics/summary - Get analytics summary")
    print("- GET /api/transaction-types - Get available transaction types")
    
    app.run(debug=True, host='0.0.0.0', port=5000
