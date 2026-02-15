"""
Warehouse Repository - Data access for warehouse operations
"""
from models.base_repository import BaseRepository

class WarehouseRepository(BaseRepository):
    """Repository for Warehouse CRUD operations"""
    
    def get_all(self, supervisor_id=None, search_term=None):
        """
        Get warehouses with filters.
        
        Args:
            supervisor_id: Filter by supervisor
            search_term: Search in name, location or supervisor name
            
        Returns:
            list: List of warehouse dicts
        """
        query = """
            SELECT 
                w.warehouse_id,
                w.warehouse_name,
                l.location_name,
                p.name AS supervisor_name,
                w.capacity,
                w.supervisor_id,
                COUNT(DISTINCT wp.product_id) AS product_count
            FROM warehouses w
            LEFT JOIN locations l ON w.location_id = l.location_id
            LEFT JOIN person p ON w.supervisor_id = p.person_id
            LEFT JOIN warehouse_products wp ON w.warehouse_id = wp.warehouse_id
            WHERE 1=1
        """
        params = []
        
        if supervisor_id:
            query += " AND w.supervisor_id = %s"
            params.append(supervisor_id)
        
        if search_term:
            query += " AND (w.warehouse_name LIKE %s OR l.location_name LIKE %s OR p.name LIKE %s)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        query += " GROUP BY w.warehouse_id ORDER BY w.warehouse_name"
        
        return self.execute_query(query, params)
    
    def get_by_id(self, wh_id):
        """Get warehouse by ID"""
        query = """
            SELECT warehouse_id, warehouse_name, location_id, supervisor_id, capacity
            FROM warehouses
            WHERE warehouse_id = %s
        """
        return self.execute_query(query, (wh_id,), fetch_one=True)
    
    def create(self, name, loc_id, supervisor_id, capacity):
        """Create new warehouse"""
        query = """
            INSERT INTO warehouses (warehouse_name, location_id, supervisor_id, capacity)
            VALUES (%s, %s, %s, %s)
        """
        return self.execute_write(query, (name, loc_id, supervisor_id, capacity))
    
    def update(self, wh_id, name, loc_id, supervisor_id, capacity):
        """Update warehouse"""
        query = """
            UPDATE warehouses 
            SET warehouse_name = %s, location_id = %s, supervisor_id = %s, capacity = %s
            WHERE warehouse_id = %s
        """
        return self.execute_write(query, (name, loc_id, supervisor_id, capacity, wh_id))
    
    def delete(self, wh_id):
        """Delete warehouse"""
        return self.execute_write("DELETE FROM warehouses WHERE warehouse_id = %s", (wh_id,))
