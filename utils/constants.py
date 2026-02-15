"""
Application Constants and Enums

This module defines all constants, enums, and permission mappings
used throughout the application. Using enums instead of magic strings
improves code maintainability and reduces typo-related bugs.
"""
from enum import Enum


class PersonType(Enum):
    """Employee/Person type classifications"""
    HOD = "HOD"
    SUPERVISOR = "SUPERVISOR"
    SALESMAN = "SALESMAN"
    GENERAL_EMPLOYEE = "GENERAL_EMPLOYEE"
    
    @classmethod
    def display_name(cls, value):
        """Get human-readable display name"""
        names = {
            cls.HOD: "Head of Department",
            cls.SUPERVISOR: "Supervisor",
            cls.SALESMAN: "Salesman",
            cls.GENERAL_EMPLOYEE: "General Employee"
        }
        return names.get(value, str(value))


class OrderStatus(Enum):
    """Order status states"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ProjectStatus(Enum):
    """Project status states"""
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ON_HOLD = "ON_HOLD"
    
    @property
    def color(self):
        """Get display color for status"""
        colors = {
            ProjectStatus.PLANNING: "#fef3c7",      # Yellow
            ProjectStatus.IN_PROGRESS: "#dbeafe",   # Blue
            ProjectStatus.COMPLETED: "#d1fae5",     # Green
            ProjectStatus.ON_HOLD: "#fee2e2"        # Red
        }
        return colors.get(self, "#ffffff")
    
    @property
    def emoji(self):
        """Get emoji for status"""
        emojis = {
            ProjectStatus.PLANNING: "🟡",
            ProjectStatus.IN_PROGRESS: "🔵",
            ProjectStatus.COMPLETED: "🟢",
            ProjectStatus.ON_HOLD: "🔴"
        }
        return emojis.get(self, "⚪")


class ApprovalStatus(Enum):
    """Work log approval status"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    
    @property
    def color(self):
        """Get display color for status"""
        colors = {
            ApprovalStatus.PENDING: "#fef3c7",   # Yellow
            ApprovalStatus.APPROVED: "#d1fae5",  # Green
            ApprovalStatus.REJECTED: "#fee2e2"   # Red
        }
        return colors.get(self, "#ffffff")


# Permission definitions for role-based access control
PERMISSIONS = {
    PersonType.HOD: [
        'view_dashboard',
        'view_employees', 'manage_employees',
        'view_departments', 'manage_departments',
        'view_projects', 'manage_projects',
        'view_warehouses', 'manage_warehouses',
        'view_products',
        'view_reports',
        'view_worklogs', 'approve_worklogs',
        'submit_worklogs'
    ],
    PersonType.SUPERVISOR: [
        'view_dashboard',
        'view_employees',
        'view_warehouses',
        'view_products', 'manage_products',
        'view_reports',
        'view_worklogs', 'approve_worklogs',
        'submit_worklogs'
    ],
    PersonType.SALESMAN: [
        'view_dashboard',
        'view_customers', 'manage_customers',
        'view_orders', 'manage_orders',
        'view_worklogs',
        'submit_worklogs'
    ],
    PersonType.GENERAL_EMPLOYEE: [
        'view_dashboard',
        'view_worklogs',
        'submit_worklogs'
    ]
}


def has_permission(user, permission):
    """
    Check if a user has a specific permission.
    
    Args:
        user: User dict with 'person_type' key
        permission: Permission string to check
        
    Returns:
        bool: True if user has permission
    """
    try:
        user_type = PersonType(user['person_type'])
        return permission in PERMISSIONS.get(user_type, [])
    except (ValueError, KeyError):
        return False


# UI Constants
COLORS = {
    'primary': '#3b82f6',
    'primary_hover': '#2563eb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#8b5cf6',
    'bg_dark': '#0f172a',
    'bg_card': '#1e293b',
    'bg_light': '#f0f0f0',
    'text_dark': '#1e293b',
    'text_muted': '#64748b',
}

# Table row limit for performance
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200
