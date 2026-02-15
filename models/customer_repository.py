"""
Customer Repository - Data access for customer operations
"""
from models.base_repository import BaseRepository

class CustomerRepository(BaseRepository):
    """Repository for Customer CRUD operations"""
    
    def get_all(self, salesman_id=None, search_term=None):
        """
        Get customers with filters.
        
        Args:
            salesman_id: Filter by assigned salesman (optional visualization aid)
            search_term: Search in name or email
            
        Returns:
            list: List of customer dicts
        """
        query = """
            SELECT 
                c.customer_id, c.name, c.email, c.phone, c.address, c.salesman_id,
                p.name AS salesman_name,
                COUNT(o.order_id) AS order_count
            FROM customers c
            LEFT JOIN person p ON c.salesman_id = p.person_id
            LEFT JOIN orders_m o ON c.customer_id = o.customer_id
            WHERE 1=1
        """
        params = []
        
        # Note: We typically show all customers but highlight own customers. 
        # But if we wanted to strictly filter:
        # if salesman_id:
        #     query += " AND c.salesman_id = %s"
        #     params.append(salesman_id)
        
        if search_term:
            query += " AND (c.name LIKE %s OR c.email LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " GROUP BY c.customer_id ORDER BY c.name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, customer_id):
        """Get customer by ID"""
        query = "SELECT * FROM customers WHERE customer_id = %s"
        return self.execute_query(query, (customer_id,), fetch_one=True)
    
    def create(self, name, email, phone, address, salesman_id):
        """Create new customer"""
        query = """
            INSERT INTO customers (name, email, phone, address, salesman_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_write(query, (name, email, phone, address, salesman_id))
    
    def update(self, customer_id, name, email, phone, address, salesman_id):
        """Update customer"""
        query = """
            UPDATE customers 
            SET name = %s, email = %s, phone = %s, address = %s, salesman_id = %s
            WHERE customer_id = %s
        """
        return self.execute_write(query, (name, email, phone, address, salesman_id, customer_id))
    
    def delete(self, customer_id):
        """Delete customer"""
        return self.execute_write("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
    
    def get_count(self, salesman_id=None):
        """Get total customer count"""
        query = "SELECT COUNT(*) as count FROM customers"
        params = []
        
        if salesman_id:
            query += " WHERE salesman_id = %s"
            params.append(salesman_id)
        
        result = self.execute_query(query, params, fetch_one=True)
        return result['count'] if result else 0
