"""
Product Repository - Data access for product operations
"""
from models.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    """Repository for Product CRUD operations"""
    
    def get_all(self, supervisor_id=None, search_term=None):
        """
        Get products with filters.
        
        Args:
            supervisor_id: Filter by supervisor (via warehouse)
            search_term: Search in name or type
            
        Returns:
            list: List of product dicts
        """
        query = """
            SELECT 
                p.product_id,
                p.product_name,
                p.product_type,
                p.unit_price,
                w.warehouse_name,
                wp.qty,
                wp.reorder_level,
                wp.warehouse_product_id,
                wp.warehouse_id
            FROM warehouse_products wp
            JOIN products p ON wp.product_id = p.product_id
            JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
            WHERE 1=1
        """
        params = []
        
        if supervisor_id:
            query += " AND w.supervisor_id = %s"
            params.append(supervisor_id)
        
        if search_term:
            query += " AND (p.product_name LIKE %s OR p.product_type LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        query += " ORDER BY w.warehouse_name, p.product_name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, product_id, warehouse_id):
        """
        Get product details for a specific warehouse.
        
        Args:
            product_id: Product ID
            warehouse_id: Warehouse ID (from warehouse_products, optional if unique product)
            
        Note: Since a product can be in multiple warehouses, we need warehouse_id 
        or we assume unique product-warehouse combo.
        """
        query = """
            SELECT 
                p.product_id, p.product_name, p.product_type, p.unit_price, p.description,
                wp.warehouse_id, wp.qty as stock_quantity, wp.reorder_level,
                w.warehouse_name
            FROM warehouse_products wp
            JOIN products p ON wp.product_id = p.product_id
            JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
            WHERE p.product_id = %s
        """
        params = [product_id]
        
        if warehouse_id:
            query += " AND wp.warehouse_id = %s"
            params.append(warehouse_id)
            
        return self.execute_query(query, params, fetch_one=True)

    def create_product(self, name, type_, price, description):
        """Create base product catalog entry"""
        query = """
            INSERT INTO products (product_name, product_type, unit_price, description)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_write(query, (name, type_, price, description))
        
    def add_to_warehouse(self, product_id, warehouse_id, qty, reorder_level):
        """Add product to warehouse inventory"""
        query = """
            INSERT INTO warehouse_products (product_id, warehouse_id, qty, reorder_level)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_write(query, (product_id, warehouse_id, qty, reorder_level))
    
    def update_product(self, product_id, name, type_, price, description):
        """Update base product details"""
        query = """
            UPDATE products 
            SET product_name = %s, product_type = %s, unit_price = %s, description = %s
            WHERE product_id = %s
        """
        return self.execute_write(query, (name, type_, price, description, product_id))
        
    def update_stock(self, product_id, warehouse_id, qty, reorder_level):
        """Update stock in warehouse"""
        query = """
            UPDATE warehouse_products 
            SET qty = %s, reorder_level = %s
            WHERE product_id = %s AND warehouse_id = %s
        """
        return self.execute_write(query, (qty, reorder_level, product_id, warehouse_id))
        
    def remove_from_warehouse(self, product_id, warehouse_id):
        """Remove product from warehouse"""
        return self.execute_write(
            "DELETE FROM warehouse_products WHERE product_id = %s AND warehouse_id = %s",
            (product_id, warehouse_id)
        )
    
    def get_low_stock_count(self):
        """Get count of items below reorder level"""
        query = "SELECT COUNT(*) as count FROM warehouse_products WHERE qty <= reorder_level"
        result = self.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    def get_low_stock_items(self, limit=10):
        """Get items with stock below reorder level"""
        query = """
            SELECT 
                p.product_id,
                p.product_name,
                w.warehouse_name,
                wp.qty,
                wp.reorder_level
            FROM warehouse_products wp
            JOIN products p ON wp.product_id = p.product_id
            JOIN warehouses w ON wp.warehouse_id = w.warehouse_id
            WHERE wp.qty <= wp.reorder_level
            ORDER BY wp.qty ASC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
