"""
Report Service

Business logic for generating reports and analytics.
"""
from models.order_repository import OrderRepository
from models.product_repository import ProductRepository
from models.customer_repository import CustomerRepository
from models.worklog_repository import WorkLogRepository
from models.employee_repository import EmployeeRepository
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportService:
    """
    Service for generating various reports and analytics.
    """
    
    def __init__(self):
        self.order_repo = OrderRepository()
        self.product_repo = ProductRepository()
        self.customer_repo = CustomerRepository()
        self.worklog_repo = WorkLogRepository()
        self.employee_repo = EmployeeRepository()
    
    def get_dashboard_metrics(self):
        """
        Get key metrics for dashboard display.
        
        Returns:
            dict: Dictionary with metric values
        """
        try:
            return {
                'total_orders': self.order_repo.get_total_count(),
                'total_revenue': self.order_repo.get_total_revenue(),
                'total_customers': self.customer_repo.get_count(),
                'low_stock_count': self.product_repo.get_low_stock_count()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            return {
                'total_orders': 0,
                'total_revenue': 0,
                'total_customers': 0,
                'low_stock_count': 0
            }
    
    def get_top_salesmen(self, limit=5):
        """Get top performing salesmen."""
        return self.order_repo.get_top_salesmen(limit)
    
    def get_low_stock_items(self, limit=10):
        """Get items with low stock."""
        return self.product_repo.get_low_stock_items(limit)
    
    def get_salesman_metrics(self, salesman_id):
        """
        Get metrics for a specific salesman.
        
        Args:
            salesman_id: Salesman person ID
            
        Returns:
            dict: Salesman-specific metrics
        """
        return {
            'total_orders': self.order_repo.get_total_count(salesman_id=salesman_id),
            'total_sales': self.order_repo.get_total_revenue(salesman_id=salesman_id),
            'customer_count': self.customer_repo.get_count(salesman_id=salesman_id)
        }
    
    def get_employee_metrics(self, employee_id, month=None, year=None):
        """
        Get metrics for a specific employee.
        
        Args:
            employee_id: Employee person ID
            month: Optional month filter
            year: Optional year filter
            
        Returns:
            dict: Employee metrics
        """
        from datetime import datetime
        
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        return {
            'hours_this_month': self.worklog_repo.get_employee_hours(
                employee_id, month=month, year=year
            )
        }
