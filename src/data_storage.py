"""
Data Storage Module for Receipt Scanner

This module handles data persistence for receipt information including:
- SQLite local storage functionality
- Google Sheets API integration setup
- Basic CRUD operations for receipts and categories
- Data export functionality

Author: Receipt Scanner Project
License: GPL-3.0
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
import csv
import io

# Optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

# Google Sheets imports (optional)
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    gspread = None
    Credentials = None

logger = logging.getLogger(__name__)

class DataStorage:
    """Handles data storage operations for receipt scanner"""
    
    def __init__(self, config):
        """
        Initialize data storage with configuration
        
        Args:
            config: Configuration object containing storage settings
        """
        self.config = config
        self.db_path = Path("receipt_data.sqlite3")
        self.google_sheets_client = None
        
        # Initialize SQLite database
        self._init_sqlite_db()
        
        # Initialize Google Sheets if configured
        if hasattr(config, 'google_sheets_enabled') and config.google_sheets_enabled:
            self._init_google_sheets()
    
    def _init_sqlite_db(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create receipts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS receipts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        raw_text TEXT,
                        total_amount REAL,
                        items_json TEXT,
                        notes TEXT,
                        image_path TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create categories table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        color TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create items table for detailed item tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        receipt_id INTEGER,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        category TEXT,
                        quantity INTEGER DEFAULT 1,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (receipt_id) REFERENCES receipts (id)
                    )
                ''')
                
                # Create expense_summary table for quick statistics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS expense_summary (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        month_year TEXT,
                        total_amount REAL,
                        item_count INTEGER,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert default categories if table is empty
                cursor.execute('SELECT COUNT(*) FROM categories')
                if cursor.fetchone()[0] == 0:
                    self._insert_default_categories(cursor)
                
                conn.commit()
                logger.info("SQLite database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    def _insert_default_categories(self, cursor):
        """Insert default expense categories"""
        default_categories = [
            ('Groceries', 'Food and household items', '#4CAF50'),
            ('Entertainment', 'Movies, games, leisure activities', '#9C27B0'),
            ('Utilities', 'Electricity, water, gas, internet', '#FF9800'),
            ('Transportation', 'Gas, public transit, parking', '#2196F3'),
            ('Healthcare', 'Medical expenses, pharmacy', '#F44336'),
            ('Dining', 'Restaurants and takeout', '#795548'),
            ('Shopping', 'Clothing, electronics, misc items', '#E91E63'),
            ('Education', 'Books, courses, school supplies', '#3F51B5'),
            ('Home & Garden', 'Home improvement, gardening', '#8BC34A'),
            ('Personal Care', 'Beauty, hygiene products', '#00BCD4'),
            ('Other', 'Miscellaneous expenses', '#607D8B')
        ]
        
        for name, description, color in default_categories:
            cursor.execute(
                'INSERT OR IGNORE INTO categories (name, description, color) VALUES (?, ?, ?)',
                (name, description, color)
            )
    
    def _init_google_sheets(self):
        """Initialize Google Sheets integration"""
        if not GOOGLE_SHEETS_AVAILABLE:
            logger.warning("Google Sheets libraries not available")
            return
        
        try:
            # This would be configured with actual credentials
            # For now, it's a placeholder for future implementation
            logger.info("Google Sheets integration placeholder initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
    
    def save_receipt(self, receipt_data: Dict) -> Optional[int]:
        """
        Save receipt data to storage
        
        Args:
            receipt_data: Dictionary containing receipt information
            
        Returns:
            Receipt ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert receipt record
                cursor.execute('''
                    INSERT INTO receipts (raw_text, total_amount, items_json, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    receipt_data.get('raw_text', ''),
                    receipt_data.get('total_amount', 0.0),
                    json.dumps(receipt_data.get('items', [])),
                    datetime.now()
                ))
                
                receipt_id = cursor.lastrowid
                
                # Insert individual items
                items = receipt_data.get('items', [])
                for item in items:
                    cursor.execute('''
                        INSERT INTO items (receipt_id, name, price, category)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        receipt_id,
                        item.get('name', ''),
                        item.get('price', 0.0),
                        item.get('category', 'Other')
                    ))
                
                # Update expense summary
                self._update_expense_summary(cursor, items)
                
                conn.commit()
                logger.info(f"Receipt saved with ID: {receipt_id}")
                
                # Sync to Google Sheets if enabled
                if self.google_sheets_client:
                    self._sync_to_google_sheets(receipt_data)
                
                return receipt_id
                
        except sqlite3.Error as e:
            logger.error(f"Error saving receipt: {e}")
            return None
    
    def get_receipt(self, receipt_id: int) -> Optional[Dict]:
        """
        Retrieve a specific receipt by ID
        
        Args:
            receipt_id: Receipt ID to retrieve
            
        Returns:
            Receipt data dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM receipts WHERE id = ?
                ''', (receipt_id,))
                
                receipt_row = cursor.fetchone()
                if not receipt_row:
                    return None
                
                # Get associated items
                cursor.execute('''
                    SELECT * FROM items WHERE receipt_id = ?
                ''', (receipt_id,))
                
                items = [dict(row) for row in cursor.fetchall()]
                
                receipt = dict(receipt_row)
                receipt['items'] = items
                
                return receipt
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving receipt {receipt_id}: {e}")
            return None
    
    def get_all_receipts(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve all receipts from storage
        
        Args:
            limit: Maximum number of receipts to return
            
        Returns:
            List of receipt dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT r.*, 
                           GROUP_CONCAT(i.name || ' ($' || i.price || ')') as item_summary
                    FROM receipts r
                    LEFT JOIN items i ON r.id = i.receipt_id
                    GROUP BY r.id
                    ORDER BY r.timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                receipts = []
                for row in cursor.fetchall():
                    receipt = dict(row)
                    
                    # Get detailed items for each receipt
                    cursor.execute('''
                        SELECT * FROM items WHERE receipt_id = ?
                    ''', (receipt['id'],))
                    
                    receipt['items'] = [dict(item_row) for item_row in cursor.fetchall()]
                    receipts.append(receipt)
                
                return receipts
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving receipts: {e}")
            return []
    
    def delete_receipt(self, receipt_id: int) -> bool:
        """
        Delete a receipt and its associated items
        
        Args:
            receipt_id: Receipt ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete associated items first
                cursor.execute('DELETE FROM items WHERE receipt_id = ?', (receipt_id,))
                
                # Delete receipt
                cursor.execute('DELETE FROM receipts WHERE id = ?', (receipt_id,))
                
                conn.commit()
                logger.info(f"Receipt {receipt_id} deleted successfully")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting receipt {receipt_id}: {e}")
            return False
    
    def _update_expense_summary(self, cursor, items: List[Dict]):
        """Update expense summary for quick statistics"""
        try:
            current_month = datetime.now().strftime('%Y-%m')
            
            for item in items:
                category = item.get('category', 'Other')
                price = item.get('price', 0.0)
                
                # Check if summary record exists
                cursor.execute('''
                    SELECT id, total_amount, item_count FROM expense_summary
                    WHERE category = ? AND month_year = ?
                ''', (category, current_month))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    new_total = existing[1] + price
                    new_count = existing[2] + 1
                    cursor.execute('''
                        UPDATE expense_summary 
                        SET total_amount = ?, item_count = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (new_total, new_count, existing[0]))
                else:
                    # Insert new record
                    cursor.execute('''
                        INSERT INTO expense_summary (category, month_year, total_amount, item_count)
                        VALUES (?, ?, ?, ?)
                    ''', (category, current_month, price, 1))
                    
        except sqlite3.Error as e:
            logger.error(f"Error updating expense summary: {e}")
    
    def get_expense_summary(self, month_year: Optional[str] = None) -> List[Dict]:
        """
        Get expense summary by category
        
        Args:
            month_year: Optional month filter (YYYY-MM format)
            
        Returns:
            List of expense summary dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if month_year:
                    cursor.execute('''
                        SELECT * FROM expense_summary 
                        WHERE month_year = ?
                        ORDER BY total_amount DESC
                    ''', (month_year,))
                else:
                    cursor.execute('''
                        SELECT category, SUM(total_amount) as total_amount, SUM(item_count) as item_count
                        FROM expense_summary
                        GROUP BY category
                        ORDER BY total_amount DESC
                    ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Error getting expense summary: {e}")
            return []
    
    def export_to_csv(self) -> Optional[str]:
        """
        Export all receipt data to CSV format
        
        Returns:
            CSV data as string or None if failed
        """
        try:
            receipts = self.get_all_receipts(limit=1000)  # Get more for export
            
            if not receipts:
                return None
            
            # Flatten data for CSV export
            rows = []
            for receipt in receipts:
                for item in receipt.get('items', []):
                    rows.append({
                        'Receipt ID': receipt['id'],
                        'Date': receipt['timestamp'],
                        'Item Name': item['name'],
                        'Price': item['price'],
                        'Category': item['category'],
                        'Receipt Total': receipt['total_amount']
                    })
            
            if not rows:
                return None
            
            # Convert to CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            
            csv_data = output.getvalue()
            output.close()
            
            logger.info(f"Exported {len(rows)} items to CSV")
            return csv_data
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    def _sync_to_google_sheets(self, receipt_data: Dict):
        """
        Sync receipt data to Google Sheets (placeholder for future implementation)
        
        Args:
            receipt_data: Receipt data to sync
        """
        # Placeholder for Google Sheets integration
        logger.info("Google Sheets sync placeholder called")
        pass
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary containing storage statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get receipt count
                cursor.execute('SELECT COUNT(*) FROM receipts')
                receipt_count = cursor.fetchone()[0]
                
                # Get total amount
                cursor.execute('SELECT SUM(total_amount) FROM receipts')
                total_amount = cursor.fetchone()[0] or 0.0
                
                # Get category distribution
                cursor.execute('''
                    SELECT category, COUNT(*) as count, SUM(price) as total
                    FROM items
                    GROUP BY category
                    ORDER BY total DESC
                ''')
                
                category_stats = [
                    {'category': row[0], 'count': row[1], 'total': row[2]}
                    for row in cursor.fetchall()
                ]
                
                return {
                    'receipt_count': receipt_count,
                    'total_amount': total_amount,
                    'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0,
                    'category_distribution': category_stats
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}