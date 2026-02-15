"""
Order Repository - Data access for order operations
"""
from models.base_repository import BaseRepository
from utils.constants import OrderStatus

class OrderRepository(BaseRepository):
    """Repository for Order CRUD operations"""
    
    def get_all(self, salesman_id=None, status=None, search_term=None):
        """
        Get orders with filters.
        
        Args:
            salesman_id: Filter by salesman
            status: Filter by status
            search_term: Search in customer name or order ID
            
        Returns:
            list: List of order dicts
        """
        query = """
            SELECT 
                o.order_id, o.order_date, o.total_amount, o.status,
                c.name AS customer_name,
                p.name AS salesman_name,
                o.salesman_id, o.customer_id
            FROM orders_m o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN person p ON o.salesman_id = p.person_id
            WHERE 1=1
        """
        params = []
        
        if salesman_id:
            query += " AND o.salesman_id = %s"
            params.append(salesman_id)
        
        if status and status != 'All':
            # Handle enum or string
            status_val = status.value if hasattr(status, 'value') else status
            query += " AND o.status = %s"
            params.append(status_val)
        
        if search_term:
            if search_term.isdigit():
                query += " AND (c.name LIKE %s OR o.order_id = %s)"
                params.extend([f"%{search_term}%", search_term])
            else:
                query += " AND c.name LIKE %s"
                params.append(f"%{search_term}%")
        
        query += " ORDER BY o.order_date DESC"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, order_id):
        """Get order by ID"""
        query = "SELECT * FROM orders_m WHERE order_id = %s"
        return self.execute_query(query, (order_id,), fetch_one=True)
    
    def get_items(self, order_id):
        """Get items for an order"""
        query = """
            SELECT oi.*, p.product_name, p.unit_price as current_price
            FROM order_items oi
            JOIN warehouse_products wp ON oi.product_id = wp.product_id AND oi.warehouse_id = wp.warehouse_id
            JOIN products p ON wp.product_id = p.product_id
            WHERE oi.order_id = %s
        """
        return self.execute_query(query, (order_id,))
    
    def create_order(self, customer_id, salesman_id, total_amount, status, order_date):
        """Create order header"""
        query = """
            INSERT INTO orders_m (customer_id, salesman_id, total_amount, status, order_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_write(query, (customer_id, salesman_id, total_amount, status, order_date))
    
    def add_item(self, order_id, warehouse_id, product_id, qty, unit_price):
        """Add item to order"""
        query = """
            INSERT INTO order_items (order_id, warehouse_id, product_id, qty, unit_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_write(query, (order_id, warehouse_id, product_id, qty, unit_price))
    
    def delete_order(self, order_id):
        """Delete order and items (cascading assumed or handled in logic)"""
        # Logic to return stock is handled in Service layer, repository just deletes
        self.execute_write("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        return self.execute_write("DELETE FROM orders_m WHERE order_id = %s", (order_id,))
    
    def get_total_count(self, salesman_id=None):
        """Get total order count"""
        query = "SELECT COUNT(*) as count FROM orders_m"
        params = []
        
        if salesman_id:
            query += " WHERE salesman_id = %s"
            params.append(salesman_id)
        
        result = self.execute_query(query, params, fetch_one=True)
        return result['count'] if result else 0
    
    def get_total_revenue(self, salesman_id=None):
        """Get total revenue from completed orders"""
        query = "SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders_m WHERE status = 'COMPLETED'"
        params = []
        
        if salesman_id:
            query += " AND salesman_id = %s"
            params.append(salesman_id)
        
        result = self.execute_query(query, params, fetch_one=True)
        return float(result['revenue']) if result else 0.0
    
    def get_top_salesmen(self, limit=5):
        """Get top performing salesmen by revenue"""
        query = """
            SELECT 
                p.person_id,
                p.name,
                COUNT(o.order_id) as order_count,
                COALESCE(SUM(o.total_amount), 0) as total_sales
            FROM person p
            JOIN salesman s ON p.person_id = s.person_id
            LEFT JOIN orders_m o ON p.person_id = o.salesman_id AND o.status = 'COMPLETED'
            WHERE p.is_active = TRUE
            GROUP BY p.person_id, p.name
            ORDER BY total_sales DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
