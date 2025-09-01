"""
Category Management Module for Receipt Scanner

This module handles expense categorization including:
- Predefined category list management
- Manual category assignment functionality
- Future ML categorization placeholder
- Category-based reporting and analytics

Author: Receipt Scanner Project
License: GPL-3.0
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from pathlib import Path
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class CategoryManager:
    """Manages expense categories and categorization logic"""
    
    def __init__(self, config):
        """
        Initialize category manager with configuration
        
        Args:
            config: Configuration object containing category settings
        """
        self.config = config
        self.db_path = Path("receipt_data.sqlite3")
        
        # Initialize category keywords for automatic categorization
        self._init_category_keywords()
        
        logger.info("Category manager initialized")
    
    def _init_category_keywords(self):
        """Initialize keywords for automatic categorization"""
        self.category_keywords = {
            'Groceries': [
                'walmart', 'kroger', 'safeway', 'publix', 'whole foods', 'trader joe',
                'market', 'grocery', 'supermarket', 'food', 'produce', 'meat', 'dairy',
                'bread', 'milk', 'eggs', 'chicken', 'beef', 'vegetables', 'fruit'
            ],
            'Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'sandwich', 'taco',
                'mcdonalds', 'subway', 'starbucks', 'kfc', 'pizza hut', 'dominos',
                'dining', 'food court', 'bistro', 'grill', 'bar', 'pub'
            ],
            'Transportation': [
                'gas', 'fuel', 'gasoline', 'shell', 'exxon', 'bp', 'chevron', 'texaco',
                'parking', 'metro', 'bus', 'transit', 'uber', 'lyft', 'taxi',
                'toll', 'bridge', 'tunnel', 'train', 'airline', 'flight'
            ],
            'Entertainment': [
                'movie', 'theater', 'cinema', 'netflix', 'spotify', 'game', 'concert',
                'amusement', 'park', 'zoo', 'museum', 'bowling', 'golf', 'gym',
                'sports', 'ticket', 'event', 'show', 'festival'
            ],
            'Shopping': [
                'amazon', 'target', 'best buy', 'macy', 'nordstrom', 'nike', 'adidas',
                'clothing', 'shoes', 'electronics', 'computer', 'phone', 'tablet',
                'clothes', 'shirt', 'pants', 'dress', 'jacket', 'accessories'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital', 'clinic',
                'doctor', 'dentist', 'medical', 'prescription', 'medicine', 'drug',
                'health', 'dental', 'vision', 'insurance', 'copay'
            ],
            'Utilities': [
                'electric', 'electricity', 'power', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone bill', 'utility', 'energy', 'heating',
                'cooling', 'trash', 'recycling'
            ],
            'Personal Care': [
                'salon', 'haircut', 'beauty', 'cosmetics', 'makeup', 'skincare',
                'spa', 'massage', 'nail', 'barber', 'shampoo', 'soap', 'perfume',
                'deodorant', 'toothpaste', 'hygiene'
            ],
            'Home & Garden': [
                'home depot', 'lowes', 'hardware', 'garden', 'plant', 'seed',
                'fertilizer', 'tools', 'paint', 'lumber', 'supplies', 'improvement',
                'repair', 'maintenance', 'lawn', 'landscape'
            ],
            'Education': [
                'school', 'university', 'college', 'tuition', 'books', 'supplies',
                'stationery', 'pen', 'pencil', 'notebook', 'textbook', 'course',
                'training', 'workshop', 'seminar'
            ]
        }
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories
        
        Returns:
            List of category names
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name FROM categories ORDER BY name')
                categories = [row[0] for row in cursor.fetchall()]
                
                # Ensure we have at least the default categories
                if not categories:
                    categories = list(self.category_keywords.keys()) + ['Other']
                
                return categories
                
        except sqlite3.Error as e:
            logger.error(f"Error getting categories: {e}")
            # Return default categories if database error
            return list(self.category_keywords.keys()) + ['Other']
    
    def add_category(self, name: str, description: str = "", color: str = "#607D8B") -> bool:
        """
        Add a new category
        
        Args:
            name: Category name
            description: Optional category description
            color: Category color for UI display
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, description, color)
                    VALUES (?, ?, ?)
                ''', (name.strip(), description.strip(), color))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Added new category: {name}")
                    return True
                else:
                    logger.warning(f"Category already exists: {name}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Error adding category {name}: {e}")
            return False
    
    def remove_category(self, name: str) -> bool:
        """
        Remove a category (and update items to 'Other')
        
        Args:
            name: Category name to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update items using this category to 'Other'
                cursor.execute('''
                    UPDATE items SET category = 'Other' WHERE category = ?
                ''', (name,))
                
                # Remove the category
                cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
                
                conn.commit()
                logger.info(f"Removed category: {name}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error removing category {name}: {e}")
            return False
    
    def suggest_category(self, item_name: str, store_name: str = "") -> str:
        """
        Suggest a category for an item based on name and store
        
        Args:
            item_name: Name of the item
            store_name: Name of the store (if available)
            
        Returns:
            Suggested category name
        """
        try:
            # Combine item name and store name for analysis
            text_to_analyze = f"{item_name} {store_name}".lower()
            
            # Score each category based on keyword matches
            category_scores = defaultdict(int)
            
            for category, keywords in self.category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text_to_analyze:
                        # Give higher score for exact matches
                        if keyword.lower() == item_name.lower():
                            category_scores[category] += 10
                        elif keyword.lower() in item_name.lower():
                            category_scores[category] += 5
                        elif keyword.lower() in store_name.lower():
                            category_scores[category] += 3
                        else:
                            category_scores[category] += 1
            
            # Return the category with the highest score
            if category_scores:
                best_category = max(category_scores, key=category_scores.get)
                logger.debug(f"Suggested category '{best_category}' for item '{item_name}'")
                return best_category
            
            # Try ML-based categorization (placeholder for future implementation)
            ml_suggestion = self._ml_categorize(item_name, store_name)
            if ml_suggestion:
                return ml_suggestion
            
            # Default to 'Other' if no matches found
            return 'Other'
            
        except Exception as e:
            logger.error(f"Error suggesting category for '{item_name}': {e}")
            return 'Other'
    
    def _ml_categorize(self, item_name: str, store_name: str = "") -> Optional[str]:
        """
        Machine learning-based categorization (placeholder for future implementation)
        
        Args:
            item_name: Name of the item
            store_name: Name of the store
            
        Returns:
            Suggested category or None
        """
        # Placeholder for future ML implementation
        # This could use scikit-learn, TensorFlow, or other ML libraries
        # to classify items based on trained models
        
        logger.debug("ML categorization not yet implemented")
        return None
    
    def bulk_categorize(self, items: List[Dict]) -> List[Dict]:
        """
        Categorize multiple items at once
        
        Args:
            items: List of item dictionaries with 'name' and optionally 'store'
            
        Returns:
            List of items with suggested categories added
        """
        try:
            categorized_items = []
            
            for item in items:
                item_copy = item.copy()
                if 'category' not in item_copy or not item_copy['category']:
                    suggested_category = self.suggest_category(
                        item_copy.get('name', ''),
                        item_copy.get('store', '')
                    )
                    item_copy['category'] = suggested_category
                    item_copy['category_confidence'] = self._calculate_confidence(
                        item_copy.get('name', ''), suggested_category
                    )
                
                categorized_items.append(item_copy)
            
            logger.info(f"Bulk categorized {len(categorized_items)} items")
            return categorized_items
            
        except Exception as e:
            logger.error(f"Error in bulk categorization: {e}")
            return items
    
    def _calculate_confidence(self, item_name: str, suggested_category: str) -> float:
        """
        Calculate confidence score for category suggestion
        
        Args:
            item_name: Name of the item
            suggested_category: Suggested category
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            if suggested_category == 'Other':
                return 0.1  # Low confidence for default category
            
            # Check for keyword matches
            keywords = self.category_keywords.get(suggested_category, [])
            item_lower = item_name.lower()
            
            exact_matches = sum(1 for keyword in keywords if keyword == item_lower)
            partial_matches = sum(1 for keyword in keywords if keyword in item_lower)
            
            if exact_matches > 0:
                return 0.9
            elif partial_matches > 0:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def get_category_stats(self) -> Dict:
        """
        Get statistics about category usage
        
        Returns:
            Dictionary containing category statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get category usage counts
                cursor.execute('''
                    SELECT category, COUNT(*) as item_count, SUM(price) as total_amount
                    FROM items
                    GROUP BY category
                    ORDER BY total_amount DESC
                ''')
                
                category_usage = []
                total_items = 0
                total_amount = 0.0
                
                for row in cursor.fetchall():
                    category_data = {
                        'category': row[0],
                        'item_count': row[1],
                        'total_amount': row[2]
                    }
                    category_usage.append(category_data)
                    total_items += row[1]
                    total_amount += row[2]
                
                # Calculate percentages
                for category_data in category_usage:
                    category_data['percentage_by_count'] = (
                        category_data['item_count'] / total_items * 100 
                        if total_items > 0 else 0
                    )
                    category_data['percentage_by_amount'] = (
                        category_data['total_amount'] / total_amount * 100 
                        if total_amount > 0 else 0
                    )
                
                return {
                    'category_usage': category_usage,
                    'total_categories': len(category_usage),
                    'total_items': total_items,
                    'total_amount': total_amount
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting category stats: {e}")
            return {}
    
    def update_category_keywords(self, category: str, keywords: List[str]) -> bool:
        """
        Update keywords for a category (for improved auto-categorization)
        
        Args:
            category: Category name
            keywords: List of keywords to associate with the category
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update in-memory keywords
            self.category_keywords[category] = [kw.lower().strip() for kw in keywords]
            
            # Store in database for persistence (could be added to schema)
            logger.info(f"Updated keywords for category '{category}': {len(keywords)} keywords")
            return True
            
        except Exception as e:
            logger.error(f"Error updating keywords for category '{category}': {e}")
            return False
    
    def export_categories(self) -> Dict:
        """
        Export category configuration for backup/sharing
        
        Returns:
            Dictionary containing all category data
        """
        try:
            categories = self.get_categories()
            stats = self.get_category_stats()
            
            export_data = {
                'categories': categories,
                'category_keywords': self.category_keywords,
                'category_stats': stats,
                'export_timestamp': logger.info("Category data exported")
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting categories: {e}")
            return {}
    
    def import_categories(self, import_data: Dict) -> bool:
        """
        Import category configuration from backup
        
        Args:
            import_data: Dictionary containing category data to import
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import categories
            categories = import_data.get('categories', [])
            for category in categories:
                if isinstance(category, str):
                    self.add_category(category)
                elif isinstance(category, dict):
                    self.add_category(
                        category.get('name', ''),
                        category.get('description', ''),
                        category.get('color', '#607D8B')
                    )
            
            # Import keywords
            keywords = import_data.get('category_keywords', {})
            for category, kw_list in keywords.items():
                self.update_category_keywords(category, kw_list)
            
            logger.info(f"Imported {len(categories)} categories and keywords")
            return True
            
        except Exception as e:
            logger.error(f"Error importing categories: {e}")
            return False