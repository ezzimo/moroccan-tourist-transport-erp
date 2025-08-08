#!/usr/bin/env python3
"""
Bootstrap Roles and Users Script for Moroccan Tourist Transport ERP

This script automates the creation of roles and demo users for testing and development.
It reads role definitions and creates corresponding database entries with proper permissions.

Usage:
    python scripts/bootstrap_roles_users.py
    python scripts/bootstrap_roles_users.py --environment production
    python scripts/bootstrap_roles_users.py --dry-run
"""

import asyncio
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add the backend app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

try:
    from sqlmodel import Session, select
    from passlib.context import CryptContext
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import uuid
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Please install: pip install sqlmodel passlib psycopg2-binary")
    sys.exit(1)

# Configure logging with maximum detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bootstrap_debug.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Enable SQL logging for psycopg2
sql_logger = logging.getLogger('psycopg2')
sql_logger.setLevel(logging.DEBUG)
sql_logger.addHandler(logging.StreamHandler(sys.stdout))

# Password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Role definitions based on the provided document
ROLE_DEFINITIONS = {
    # Administration Roles
    "super_admin": {
        "name": "super_admin",
        "description": "System Super Admin with full access to all tenant data, settings, and audit logs",
        "permissions": [
            "auth:create", "auth:read", "auth:update",
            "auth:delete",
            "tenant:create", "tenant:read", "tenant:update", "tenant:delete",
            "users:create", "users:read", "users:update", "users:delete",
            "roles:create", "roles:read", "roles:update", "roles:delete",
            "permissions:create", "permissions:read", "permissions:update",
            "permissions:delete",
            "bookings:create", "bookings:read", "bookings:update",
            "bookings:delete",
            "routes:create", "routes:read", "routes:update", "routes:delete",
            "assignments:create", "assignments:read", "assignments:update",
            "assignments:delete",
            "drivers:create", "drivers:read", "drivers:update",
            "drivers:delete",
            "schedules:create", "schedules:read", "schedules:update",
            "schedules:delete",
            "planning:create", "planning:read", "planning:update",
            "planning:delete",
            "reservations:create", "reservations:read", "reservations:update",
            "reservations:delete",
            "pricing:create", "pricing:read", "pricing:update",
            "pricing:delete",
            "customers:create", "customers:read", "customers:update",
            "customers:delete",
            "contracts:create", "contracts:read", "contracts:update",
            "contracts:delete",
            "feedback:create", "feedback:read", "feedback:update",
            "feedback:delete",
            "vehicles:create", "vehicles:read", "vehicles:update",
            "vehicles:delete",
            "maintenance:create", "maintenance:read", "maintenance:update",
            "maintenance:delete",
            "fuel:create", "fuel:read", "fuel:update", "fuel:delete",
            "profile:read",
            "documents:upload",
            "tasks:read",
            "incidents:create", "incidents:read", "incidents:update",
            "incidents:delete",
            "employees:create", "employees:read", "employees:update",
            "employees:delete",
            "training:create", "training:read", "training:update",
            "training:delete",
            "recruitment:create", "recruitment:read", "recruitment:update",
            "recruitment:delete",
            "applications:create", "applications:read", "applications:update",
            "applications:delete",
            "jobs:create", "jobs:read", "jobs:update", "jobs:delete",
            "invoices:create", "invoices:read", "invoices:update",
            "invoices:delete",
            "payments:create", "payments:read", "payments:update",
            "payments:delete",
            "expenses:create", "expenses:read", "expenses:update",
            "expenses:delete",
            "tax_reports:create", "tax_reports:read", "tax_reports:update",
            "tax_reports:delete",
            "reports:read", "ledgers:read",
            "inventory:create", "inventory:read", "inventory:update",
            "inventory:delete",
            "suppliers:create", "suppliers:read", "suppliers:update",
            "suppliers:delete",
            "purchase_orders:create", "purchase_orders:read",
            "purchase_orders:update", "purchase_orders:delete",
            "stock_movements:create", "stock_movements:read",
            "stock_movements:update", "stock_movements:delete",
            "deliveries:update",
            "audits:create", "audits:read", "audits:update", "audits:delete",
            "nonconformities:create", "nonconformities:read",
            "nonconformities:update", "nonconformities:delete",
            "quality:create", "quality:read", "quality:update",
            "quality:delete",
            "compliance:create", "compliance:read", "compliance:update",
            "compliance:delete",
            "certifications:create", "certifications:read",
            "certifications:update", "certifications:delete",
            "alerts:create",
            "notifications:send", "notifications:create", "notifications:read",
            "notifications:update", "notifications:delete",
            "templates:create", "templates:read", "templates:update",
            "templates:delete",
            "campaigns:create", "campaigns:read", "campaigns:update",
            "campaigns:delete",
            "messages:create", "messages:read", "messages:update",
            "messages:delete",
        ],
        "labels": {
            "en": "System Super Admin",
            "fr": "Super Administrateur Système",
            "ar": "المشرف العام للنظام"
        }
    },
    "tenant_admin": {
        "name": "tenant_admin",
        "description": "Company Admin with full control of a company's instance, users, and services",
        "permissions": [
            "tenant:create", "tenant:read", "tenant:update",
            "tenant:delete",
            "users:create", "users:read", "users:update",
            "users:delete",
            "roles:create", "roles:read", "roles:update",
            "roles:delete",
        ],
        "labels": {
            "en": "Company Admin",
            "fr": "Administrateur de l'entreprise",
            "ar": "مشرف الشركة"
        }
    },
    "role_manager": {
        "name": "role_manager",
        "description": "Can create/edit roles and assign permissions",
        "permissions": [
            "roles:create", "roles:read", "roles:update", "roles:delete",
            "permissions:create", "permissions:read", "permissions:update",
            "permissions:delete",
        ],
        "labels": {
            "en": "Role Manager",
            "fr": "Gestionnaire des rôles",
            "ar": "مدير الصلاحيات"
        }
    },

    # Operational Roles
    "dispatcher": {
        "name": "dispatcher",
        "description": "Manage bookings, routes, driver assignments",
        "permissions": [
            "bookings:create", "bookings:read", "bookings:update",
            "bookings:delete",
            "routes:create", "routes:read", "routes:update",
            "routes:delete",
            "assignments:create", "assignments:read", "assignments:update",
            "assignments:delete",
            "drivers:read",
        ],
        "labels": {
            "en": "Dispatcher",
            "fr": "Dispatcheur",
            "ar": "مسؤول الجدولة"
        }
    },
    "route_planner": {
        "name": "route_planner",
        "description": "Create/edit route templates, scheduling",
        "permissions": [
            "routes:create", "routes:read", "routes:update",
            "routes:delete",
            "schedules:create", "schedules:read", "schedules:update",
            "schedules:delete",
            "planning:create", "planning:read", "planning:update",
            "planning:delete",
        ],
        "labels": {
            "en": "Route Planner",
            "fr": "Planificateur des trajets",
            "ar": "مخطط المسارات"
        }
    },
    "booking_manager": {
        "name": "booking_manager",
        "description": "Approve/reschedule/cancel reservations",
        "permissions": [
            "bookings:create", "bookings:read", "bookings:update",
            "bookings:delete",
            "reservations:create", "reservations:read", "reservations:update",
            "reservations:delete",
            "pricing:read",
        ],
        "labels": {
            "en": "Booking Manager",
            "fr": "Responsable des réservations",
            "ar": "مدير الحجوزات"
        }
    },
    "client_account_manager": {
        "name": "client_account_manager",
        "description": "Handle key clients, contract terms, special requests",
        "permissions": [
            "customers:create", "customers:read", "customers:update",
            "customers:delete",
            "contracts:create", "contracts:read", "contracts:update",
            "contracts:delete",
            "feedback:read",
        ],
        "labels": {
            "en": "Client Account Manager",
            "fr": "Gestionnaire de comptes client",
            "ar": "مدير حسابات العملاء"
        }
    },
    
    # Fleet Roles
    "fleet_manager": {
        "name": "fleet_manager",
        "description": "Manage vehicles, assignments, compliance",
        "permissions": [
            "vehicles:create", "vehicles:read", "vehicles:update",
            "vehicles:delete",
            "maintenance:create", "maintenance:read", "maintenance:update",
            "maintenance:delete",
            "fuel:create", "fuel:read", "fuel:update", "fuel:delete",
            "assignments:create", "assignments:read", "assignments:update",
            "assignments:delete",
        ],
        "labels": {
            "en": "Fleet Manager",
            "fr": "Gestionnaire de flotte",
            "ar": "مدير الأسطول"
        }
    },
    "maintenance_tech": {
        "name": "maintenance_tech",
        "description": "View/update maintenance records, schedules",
        "permissions": ["maintenance:read", "maintenance:update", "vehicles:read"],
        "labels": {
            "en": "Maintenance Technician",
            "fr": "Technicien de maintenance",
            "ar": "فني الصيانة"
        }
    },
    "fuel_log_manager": {
        "name": "fuel_log_manager",
        "description": "Log fuel usage, monitor efficiency",
        "permissions": ["fuel:create", "fuel:read", "fuel:update"],
        "labels": {
            "en": "Fuel Log Manager",
            "fr": "Responsable carburant",
            "ar": "مسؤول سجلات الوقود"
        }
    },
    
    # Driver Roles
    "driver": {
        "name": "driver",
        "description": "Mobile app: see tasks, upload documents, report issues",
        "permissions": ["profile:read", "documents:upload", "tasks:read", "incidents:create"],
        "labels": {
            "en": "Driver",
            "fr": "Chauffeur",
            "ar": "السائق"
        }
    },
    "lead_driver": {
        "name": "lead_driver",
        "description": "Driver + ability to supervise/co-sign incidents",
        "permissions": [
            "profile:read",
            "documents:upload",
            "tasks:read",
            "incidents:create", "incidents:read", "incidents:update",
            "incidents:delete",
            "drivers:read",
        ],
        "labels": {
            "en": "Lead Driver",
            "fr": "Chef Chauffeur",
            "ar": "السائق الرئيسي"
        }
    },
    
    # HR & Staff Roles
    "hr_manager": {
        "name": "hr_manager",
        "description": "Manage employees, contracts, leaves, training",
        "permissions": [
            "employees:create", "employees:read", "employees:update",
            "employees:delete",
            "contracts:create", "contracts:read", "contracts:update",
            "contracts:delete",
            "training:create", "training:read", "training:update",
            "training:delete",
            "recruitment:read",
        ],
        "labels": {
            "en": "HR Manager",
            "fr": "Responsable RH",
            "ar": "مدير الموارد البشرية"
        }
    },
    "recruiter": {
        "name": "recruiter",
        "description": "Post jobs, manage applications",
        "permissions": [
            "recruitment:create", "recruitment:read", "recruitment:update",
            "recruitment:delete",
            "applications:create", "applications:read", "applications:update",
            "applications:delete",
            "jobs:create", "jobs:read", "jobs:update",
            "jobs:delete",
        ],
        "labels": {
            "en": "Recruiter",
            "fr": "Recruteur",
            "ar": "مسؤول التوظيف"
        }
    },
    "trainer": {
        "name": "trainer",
        "description": "Assign and track driver/staff training",
        "permissions": [
            "training:create", "training:read", "training:update",
            "training:delete",
            "certifications:create", "certifications:read", "certifications:update",
            "certifications:delete",
            "employees:read"
        ],
        "labels": {
            "en": "Trainer",
            "fr": "Formateur",
            "ar": "المدرب"
        }
    },
    
    # Finance Roles
    "finance_manager": {
        "name": "finance_manager",
        "description": "Full access to invoices, expenses, tax reports",
        "permissions": [
            "invoices:create", "invoices:read", "invoices:update",
            "invoices:delete",
            "payments:create", "payments:read", "payments:update",
            "payments:delete",
            "expenses:create", "expenses:read", "expenses:update",
            "expenses:delete",
            "tax_reports:create", "tax_reports:read", "tax_reports:update",
            "tax_reports:delete",
        ],
        "labels": {
            "en": "Finance Manager",
            "fr": "Responsable financier",
            "ar": "المدير المالي"
        }
    },
    "billing_agent": {
        "name": "billing_agent",
        "description": "Issue invoices, track payments",
        "permissions": [
            "invoices:create", "invoices:read",
            "payments:create", "payments:read",
        ],
        "labels": {
            "en": "Billing Agent",
            "fr": "Agent de facturation",
            "ar": "مسؤول الفوترة"
        }
    },
    "accountant": {
        "name": "accountant",
        "description": "View ledgers, manage financial reports",
        "permissions": [
            "reports:read",
            "ledgers:read",
            "invoices:read",
            "payments:read",
        ],
        "labels": {
            "en": "Accountant",
            "fr": "Comptable",
            "ar": "محاسب"
        }
    },
    
    # Inventory Roles
    "inventory_manager": {
        "name": "inventory_manager",
        "description": "Manage items, suppliers, purchase orders",
        "permissions": [
            "inventory:create", "inventory:read", "inventory:update",
            "inventory:delete",
            "suppliers:create", "suppliers:read", "suppliers:update",
            "suppliers:delete",
            "purchase_orders:create", "purchase_orders:read",
            "purchase_orders:update", "purchase_orders:delete",
        ],
        "labels": {
            "en": "Inventory Manager",
            "fr": "Responsable des stocks",
            "ar": "مدير المخزون"
        }
    },
    "warehouse_staff": {
        "name": "warehouse_staff",
        "description": "Record movements, confirm deliveries",
        "permissions": [
            "inventory:read",
            "stock_movements:create", "stock_movements:read",
            "stock_movements:update", "stock_movements:delete",
            "deliveries:update",
        ],
        "labels": {
            "en": "Warehouse Staff",
            "fr": "Magasinier",
            "ar": "موظف المستودع"
        }
    },
    
    # QA & Compliance Roles
    "qa_officer": {
        "name": "qa_officer",
        "description": "Run audits, manage non-conformities",
        "permissions": [
            "audits:create", "audits:read", "audits:update", "audits:delete",
            "nonconformities:create", "nonconformities:read",
            "nonconformities:update", "nonconformities:delete",
            "quality:create", "quality:read", "quality:update",
            "quality:delete",
        ],
        "labels": {
            "en": "QA Officer",
            "fr": "Agent qualité",
            "ar": "مسؤول الجودة"
        }
    },
    "compliance_officer": {
        "name": "compliance_officer",
        "description": "Track certifications, vehicle/driver document compliance",
        "permissions": [
            "compliance:create", "compliance:read", "compliance:update",
            "compliance:delete",
            "certifications:create", "certifications:read",
            "certifications:update", "certifications:delete",
            "documents:read",
        ],
        "labels": {
            "en": "Compliance Officer",
            "fr": "Agent conformité",
            "ar": "مسؤول المطابقة"
        }
    },
    
    # Customer & Client Roles
    "corporate_client_admin": {
        "name": "corporate_client_admin",
        "description": "Book/manage trips for company employees",
        "permissions": [
            "bookings:create", "bookings:read",
            "employees:read", "invoices:read"
        ],
        "labels": {
            "en": "Corporate Client Admin",
            "fr": "Admin Client Entreprise",
            "ar": "مدير عميل مؤسسي"
        }
    },
    "client_user": {
        "name": "client_user",
        "description": "View trips, invoices, submit feedback",
        "permissions": [
            "bookings:read:own", "invoices:read:own", "feedback:create",
        ],
        "labels": {
            "en": "Individual Client",
            "fr": "Client Individuel",
            "ar": "عميل فردي"
        }
    },
    
    # Communication Roles
    "communication_manager": {
        "name": "communication_manager",
        "description": "Create/manage notification templates, campaigns",
        "permissions": [
            "notifications:create", "notifications:read", "notifications:update",
            "notifications:delete",
            "templates:create", "templates:read", "templates:update",
            "templates:delete",
            "campaigns:create", "campaigns:read", "campaigns:update",
            "campaigns:delete",
        ],
        "labels": {
            "en": "Communication Manager",
            "fr": "Responsable communication",
            "ar": "مسؤول التواصل"
        }
    },
    "alert_dispatcher": {
        "name": "alert_dispatcher",
        "description": "Trigger real-time messages (delays, issues, etc.)",
        "permissions": [
            "alerts:create", "notifications:send",
            "messages:create", "messages:read", "messages:update",
            "messages:delete",
        ],
        "labels": {
            "en": "Alert Dispatcher",
            "fr": "Envoyeur d'alertes",
            "ar": "مرسل التنبيهات"
        }
    }
}

# Demo user definitions
DEMO_USERS = [
    {
        "email": "superadmin@example.com",
        "full_name": "System Super Administrator",
        "phone": "+212600000001",
        "password": "SuperAdmin123!",
        "roles": ["super_admin"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "admin@example.com",
        "full_name": "Company Administrator",
        "phone": "+212600000002",
        "password": "Admin123!",
        "roles": ["tenant_admin"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "dispatcher@example.com",
        "full_name": "Operations Dispatcher",
        "phone": "+212600000003",
        "password": "Dispatcher123!",
        "roles": ["dispatcher"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "fleetmanager@example.com",
        "full_name": "Fleet Manager",
        "phone": "+212600000004",
        "password": "Fleet123!",
        "roles": ["fleet_manager"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "driver@example.com",
        "full_name": "Demo Driver",
        "phone": "+212600000005",
        "password": "Driver123!",
        "roles": ["driver"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "hrmanager@example.com",
        "full_name": "HR Manager",
        "phone": "+212600000006",
        "password": "HR123!",
        "roles": ["hr_manager"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "financemanager@example.com",
        "full_name": "Finance Manager",
        "phone": "+212600000007",
        "password": "Finance123!",
        "roles": ["finance_manager"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "inventorymanager@example.com",
        "full_name": "Inventory Manager",
        "phone": "+212600000008",
        "password": "Inventory123!",
        "roles": ["inventory_manager"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "qaofficer@example.com",
        "full_name": "QA Officer",
        "phone": "+212600000009",
        "password": "QA123!",
        "roles": ["qa_officer"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    },
    {
        "email": "client@example.com",
        "full_name": "Demo Client",
        "phone": "+212600000010",
        "password": "Client123!",
        "roles": ["client_user"],
        "is_verified": True,
        "is_active": True,
        "must_change_password": False,
        "is_locked": False,
        "avatar_url": None,
    }
]


class DatabaseConnection:
    """Database connection manager with detailed logging"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.connection = None
        logger.debug(f"🔧 Initializing DatabaseConnection for environment: {environment}")
        
    def get_db_config(self) -> Dict[str, str]:
        """Get database configuration based on environment"""
        logger.debug(f"📋 Getting database configuration for environment: {self.environment}")
        
        if self.environment == "production":
            config = {
                "host": os.getenv("DB_HOST", "db_auth"),
                "port": int(os.getenv("DB_PORT", "5432")),
                "database": os.getenv("DB_NAME", "auth_db"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "password")
            }
            logger.debug(f"🏭 Production config: host={config['host']}, port={config['port']}, database={config['database']}, user={config['user']}")
        else:
            # Development/testing configuration
            config = {
                "host": "db_auth",
                "port": 5432,
                "database": "auth_db",
                "user": "postgres",
                "password": "password"
            }
            logger.debug(f"🛠️ Development config: host={config['host']}, port={config['port']}, database={config['database']}, user={config['user']}")
        
        return config
    
    def connect(self) -> psycopg2.extensions.connection:
        """Establish database connection with detailed logging"""
        if self.connection is None:
            config = self.get_db_config()
            logger.info(f"🔌 Attempting to connect to database...")
            logger.debug(f"🔍 Connection parameters: {config['host']}:{config['port']}/{config['database']} as {config['user']}")
            
            try:
                start_time = datetime.utcnow()
                self.connection = psycopg2.connect(**config)
                connection_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Test the connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()[0]
                cursor.close()
                
                logger.info(f"✅ Connected to database: {config['database']}@{config['host']} in {connection_time:.3f}s")
                logger.debug(f"🗄️ Database version: {db_version}")
                
                # Log connection info
                logger.debug(f"🔗 Connection info:")
                logger.debug(f"   - Server version: {self.connection.server_version}")
                logger.debug(f"   - Protocol version: {self.connection.protocol_version}")
                logger.debug(f"   - Encoding: {self.connection.encoding}")
                logger.debug(f"   - Status: {self.connection.status}")
                
            except psycopg2.Error as e:
                logger.error(f"❌ Database connection failed: {e}")
                logger.debug(f"🔍 Error details: {type(e).__name__}: {str(e)}")
                logger.debug(f"🔍 Connection config used: {config}")
                raise
                
        return self.connection
    
    def close(self):
        """Close database connection with logging"""
        if self.connection:
            logger.debug("🔌 Closing database connection...")
            self.connection.close()
            self.connection = None
            logger.debug("✅ Database connection closed")


class RoleUserBootstrap:
    """Main bootstrap class for roles and users with comprehensive logging"""
    
    def __init__(self, db_connection: DatabaseConnection, dry_run: bool = False):
        self.db = db_connection
        self.dry_run = dry_run
        self.created_roles = []
        self.created_users = []
        self.execution_stats = {
            'start_time': datetime.utcnow(),
            'sql_queries_executed': 0,
            'roles_processed': 0,
            'users_processed': 0,
            'permissions_created': 0,
            'role_assignments': 0
        }
        
        logger.info(f"🚀 Initializing RoleUserBootstrap (dry_run={dry_run})")
        logger.debug(f"📊 Execution stats initialized: {self.execution_stats}")
        
    def log_sql_execution(self, query: str, params: tuple = None, execution_time: float = None):
        """Log SQL execution details"""
        self.execution_stats['sql_queries_executed'] += 1
        
        if self.dry_run:
            logger.info(f"[DRY RUN] 📝 SQL Query #{self.execution_stats['sql_queries_executed']}")
            logger.info(f"[DRY RUN] 🔍 Query: {query.strip()}")
            if params:
                logger.info(f"[DRY RUN] 📋 Parameters: {params}")
        else:
            logger.debug(f"🔍 Executing SQL Query #{self.execution_stats['sql_queries_executed']}")
            logger.debug(f"📝 Query: {query.strip()}")
            if params:
                logger.debug(f"📋 Parameters: {params}")
            if execution_time:
                logger.debug(f"⏱️ Execution time: {execution_time:.3f}s")
        
    def execute_sql(self, query: str, params: tuple = None) -> Optional[List]:
        """Execute SQL query with comprehensive logging"""
        start_time = datetime.utcnow()
        
        self.log_sql_execution(query, params)
        
        if self.dry_run:
            logger.debug(f"[DRY RUN] ⏭️ Skipping actual execution")
            return None
            
        conn = self.db.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            logger.debug(f"🔄 Executing query...")
            cursor.execute(query, params)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                logger.debug(f"📊 Query returned {len(result)} rows in {execution_time:.3f}s")
                if result and len(result) <= 5:  # Log small result sets
                    logger.debug(f"📋 Result: {result}")
                return result
            else:
                affected_rows = cursor.rowcount
                conn.commit()
                logger.debug(f"✅ Query executed successfully, {affected_rows} rows affected in {execution_time:.3f}s")
                return None
                
        except psycopg2.Error as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            conn.rollback()
            logger.error(f"❌ SQL execution failed after {execution_time:.3f}s: {e}")
            logger.debug(f"🔍 Error details:")
            logger.debug(f"   - Error type: {type(e).__name__}")
            logger.debug(f"   - Error message: {str(e)}")
            logger.debug(f"   - Query: {query}")
            logger.debug(f"   - Parameters: {params}")
            raise
        finally:
            cursor.close()
    
    def role_exists(self, role_name: str) -> bool:
        """Check if role already exists with logging"""
        logger.debug(f"🔍 Checking if role exists: {role_name}")
        query = "SELECT id FROM role WHERE name = %s"
        result = self.execute_sql(query, (role_name,))
        exists = bool(result) if result is not None else False
        logger.debug(f"📋 Role '{role_name}' exists: {exists}")
        return exists
    
    def user_exists(self, email: str) -> bool:
        """Check if user already exists with logging"""
        logger.debug(f"🔍 Checking if user exists: {email}")
        query = "SELECT id FROM users WHERE email = %s"
        result = self.execute_sql(query, (email,))
        exists = bool(result) if result is not None else False
        logger.debug(f"📋 User '{email}' exists: {exists}")
        return exists
    
    def create_role(self, role_data: Dict) -> str:
        """Create a new role with detailed logging"""
        role_id = str(uuid.uuid4()).replace('-', '')
        created_at = datetime.utcnow()
        
        logger.info(f"🔧 Creating role: {role_data['name']}")
        logger.debug(f"📋 Role details:")
        logger.debug(f"   - ID: {role_id}")
        logger.debug(f"   - Name: {role_data['name']}")
        logger.debug(f"   - Description: {role_data['description']}")
        logger.debug(f"   - Permissions: {role_data.get('permissions', [])}")
        logger.debug(f"   - Labels: {role_data.get('labels', {})}")
        
        query = """
            INSERT INTO role (id, name, description, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (
            role_id,
            role_data['name'],
            role_data['description'],
            created_at,
            created_at
        )
        
        self.execute_sql(query, params)
        self.execution_stats['roles_processed'] += 1
        
        if not self.dry_run:
            logger.info(f"✅ Created role: {role_data['name']} (ID: {role_id})")
            self.created_roles.append(role_data['name'])
        else:
            logger.info(f"[DRY RUN] ✅ Would create role: {role_data['name']}")
        
        return role_id
    
    def create_permissions(self, role_id: str, permissions: List[str]):
        """Create permissions for a role with detailed logging"""
        logger.info(f"🔐 Creating {len(permissions)} permissions for role ID: {role_id}")
        
        for i, permission in enumerate(permissions, 1):
            logger.debug(f"🔐 Processing permission {i}/{len(permissions)}: {permission}")
            
            # Parse permission string (e.g., "vehicles:create" -> service="vehicles", action="create")
            if ':' in permission:
                parts = permission.split(':', 1)
                service_name = parts[0]
                action_part = parts[1]
                
                if action_part == "*":
                    action = "*"
                    resource = "all"
                elif ':' in action_part:
                    action_parts = action_part.split(':', 1)
                    action = action_parts[0]
                    resource = action_parts[1]
                else:
                    action = action_part
                    resource = "all"
            else:
                service_name = permission
                action = "read"
                resource = "all"
            
            logger.debug(f"📋 Parsed permission: service={service_name}, action={action}, resource={resource}")
            
            # Create permission if it doesn't exist
            perm_id = str(uuid.uuid4()).replace('-', '')
            created_at = datetime.utcnow()
            
            # Check if permission exists
            check_query = """
                SELECT id FROM permissions 
                WHERE service_name = %s AND action = %s AND resource = %s
            """
            existing = self.execute_sql(check_query, (service_name, action, resource))
            
            if not existing:
                logger.debug(f"🆕 Creating new permission: {service_name}:{action}:{resource}")
                perm_query = """
                    INSERT INTO permissions (id, service_name, action, resource, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """
                self.execute_sql(perm_query, (perm_id, service_name, action, resource, created_at))
                self.execution_stats['permissions_created'] += 1
                
                if not self.dry_run:
                    logger.debug(f"✅ Created permission: {service_name}:{action}:{resource} (ID: {perm_id})")
            else:
                perm_id = existing[0]['id'] if existing else perm_id
                logger.debug(f"♻️ Using existing permission: {service_name}:{action}:{resource} (ID: {perm_id})")
            
            # Link role to permission
            logger.debug(f"🔗 Linking role {role_id} to permission {perm_id}")
            role_perm_query = """
                INSERT INTO rolepermission (role_id, permission_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """
            self.execute_sql(role_perm_query, (role_id, perm_id))
            
            if not self.dry_run:
                logger.debug(f"✅ Linked role to permission")
    
    def create_user(self, user_data: Dict) -> str:
        """Create a new user with detailed logging"""
        user_id = str(uuid.uuid4()).replace('-', '')
        
        logger.info(f"👤 Creating user: {user_data['email']}")
        logger.debug(f"📋 User details:")
        logger.debug(f"   - ID: {user_id}")
        logger.debug(f"   - Full name: {user_data['full_name']}")
        logger.debug(f"   - Email: {user_data['email']}")
        logger.debug(f"   - Phone: {user_data['phone']}")
        logger.debug(f"   - Roles: {user_data.get('roles', [])}")
        logger.debug(f"   - Is verified: {user_data.get('is_verified', False)}")
        
        # 🔐 Hash password
        logger.debug(f"🔐 Hashing password...")
        hash_start = datetime.utcnow()
        password_hash = pwd_context.hash(user_data['password'])
        hash_time = (datetime.utcnow() - hash_start).total_seconds()
        logger.debug(f"🔐 Password hashed in {hash_time:.3f}s")
        
        created_at = datetime.utcnow()

        # ✅ Ensure all required fields are inserted (no nulls in NOT NULL columns)
        query = """
            INSERT INTO users (
                id, full_name, email, phone, password_hash, 
                is_active, is_verified, is_locked, must_change_password,
                avatar_url, failed_login_attempts, last_login_at,
                created_at, updated_at, last_login, deleted_at
            )
            VALUES (%s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, 
                    %s, %s, %s, 
                    %s, %s, %s, %s)
        """
        
        params = (
            user_id,
            user_data['full_name'],
            user_data['email'],
            user_data['phone'],
            password_hash,
            True,                                # is_active
            user_data.get('is_verified', False), # is_verified
            False,                               # is_locked
            False,                               # must_change_password
            user_data.get('avatar_url', None),   # avatar_url
            0,                                   # failed_login_attempts
            None,                                # last_login_at
            created_at,                          # created_at
            None,                                # updated_at
            None,                                # last_login
            None                                 # deleted_at
        )
        
        self.execute_sql(query, params)
        self.execution_stats['users_processed'] += 1
        
        if not self.dry_run:
            logger.info(f"✅ Created user: {user_data['email']} (ID: {user_id})")
            self.created_users.append(user_data['email'])
        else:
            logger.info(f"[DRY RUN] ✅ Would create user: {user_data['email']}")
        
        return user_id

    
    def assign_user_roles(self, user_id: str, role_names: List[str]):
        """Assign roles to a user with detailed logging"""
        logger.info(f"🔗 Assigning {len(role_names)} roles to user ID: {user_id}")
        
        for i, role_name in enumerate(role_names, 1):
            logger.debug(f"🔗 Processing role assignment {i}/{len(role_names)}: {role_name}")
            
            # Get role ID
            role_query = "SELECT id FROM role WHERE name = %s"
            role_result = self.execute_sql(role_query, (role_name,))
            
            if role_result:
                role_id = role_result[0]['id']
                logger.debug(f"📋 Found role '{role_name}' with ID: {role_id}")
                
                # Assign role to user
                user_role_query = """
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """
                self.execute_sql(user_role_query, (user_id, role_id))
                self.execution_stats['role_assignments'] += 1
                
                if not self.dry_run:
                    logger.info(f"✅ Assigned role '{role_name}' to user")
                else:
                    logger.info(f"[DRY RUN] ✅ Would assign role '{role_name}' to user")
            else:
                logger.warning(f"⚠️ Role '{role_name}' not found, skipping assignment")
    
    def bootstrap_roles(self):
        """Bootstrap all roles with comprehensive logging"""
        logger.info("🔧 Starting roles bootstrap process...")
        logger.info(f"📊 Total roles to process: {len(ROLE_DEFINITIONS)}")
        
        start_time = datetime.utcnow()
        processed_count = 0
        skipped_count = 0
        
        for role_name, role_data in ROLE_DEFINITIONS.items():
            processed_count += 1
            logger.info(f"🔄 Processing role {processed_count}/{len(ROLE_DEFINITIONS)}: {role_name}")
            
            if self.role_exists(role_name):
                logger.info(f"⏭️ Role '{role_name}' already exists, skipping")
                skipped_count += 1
                continue
            
            role_id = self.create_role(role_data)
            
            # Create permissions for the role
            if 'permissions' in role_data and role_data['permissions']:
                logger.debug(f"🔐 Creating permissions for role '{role_name}'")
                self.create_permissions(role_id, role_data['permissions'])
            else:
                logger.debug(f"ℹ️ No permissions defined for role '{role_name}'")
        
        bootstrap_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✅ Roles bootstrap completed in {bootstrap_time:.3f}s")
        logger.info(f"📊 Summary: {len(self.created_roles)} created, {skipped_count} skipped")
    
    def bootstrap_users(self):
        """Bootstrap demo users with comprehensive logging"""
        logger.info("👥 Starting users bootstrap process...")
        logger.info(f"📊 Total users to process: {len(DEMO_USERS)}")
        
        start_time = datetime.utcnow()
        processed_count = 0
        skipped_count = 0
        
        for user_data in DEMO_USERS:
            processed_count += 1
            logger.info(f"🔄 Processing user {processed_count}/{len(DEMO_USERS)}: {user_data['email']}")
            
            if self.user_exists(user_data['email']):
                logger.info(f"⏭️ User '{user_data['email']}' already exists, skipping")
                skipped_count += 1
                continue
            
            user_id = self.create_user(user_data)
            
            # Assign roles to user
            if 'roles' in user_data and user_data['roles']:
                logger.debug(f"🔗 Assigning roles to user '{user_data['email']}'")
                self.assign_user_roles(user_id, user_data['roles'])
            else:
                logger.debug(f"ℹ️ No roles defined for user '{user_data['email']}'")
        
        bootstrap_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✅ Users bootstrap completed in {bootstrap_time:.3f}s")
        logger.info(f"📊 Summary: {len(self.created_users)} created, {skipped_count} skipped")
    
    def log_execution_summary(self):
        """Log comprehensive execution summary"""
        total_time = (datetime.utcnow() - self.execution_stats['start_time']).total_seconds()
        
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"⏱️ Total execution time: {total_time:.3f}s")
        logger.info(f"🔍 SQL queries executed: {self.execution_stats['sql_queries_executed']}")
        logger.info(f"🔧 Roles processed: {self.execution_stats['roles_processed']}")
        logger.info(f"👥 Users processed: {self.execution_stats['users_processed']}")
        logger.info(f"🔐 Permissions created: {self.execution_stats['permissions_created']}")
        logger.info(f"🔗 Role assignments: {self.execution_stats['role_assignments']}")
        logger.info(f"📈 Average query time: {total_time / max(self.execution_stats['sql_queries_executed'], 1):.3f}s")
        logger.info("=" * 50)
        
        if self.created_roles:
            logger.info("🔧 Created roles:")
            for role in self.created_roles:
                logger.info(f"   ✅ {role}")
        
        if self.created_users:
            logger.info("👥 Created users:")
            for user_email in self.created_users:
                user_data = next(u for u in DEMO_USERS if u['email'] == user_email)
                logger.info(f"   ✅ {user_email} (roles: {', '.join(user_data['roles'])})")
    
    def run_bootstrap(self):
        """Run the complete bootstrap process with comprehensive logging"""
        logger.info("🚀 Starting role and user bootstrap process...")
        logger.info(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        logger.info(f"📅 Start time: {self.execution_stats['start_time']}")
        
        try:
            # Bootstrap roles first
            logger.info("🎯 Phase 1: Bootstrapping roles...")
            self.bootstrap_roles()
            
            # Then bootstrap users
            logger.info("🎯 Phase 2: Bootstrapping users...")
            self.bootstrap_users()
            
            # Log comprehensive summary
            self.log_execution_summary()
            
            logger.info("🎉 Bootstrap process completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Bootstrap process failed: {e}")
            logger.debug(f"🔍 Exception details:", exc_info=True)
            self.log_execution_summary()
            raise


def main():
    """Main entry point with comprehensive logging"""
    parser = argparse.ArgumentParser(
        description="Bootstrap roles and users for Moroccan Tourist Transport ERP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/bootstrap_roles_users.py
  python3 scripts/bootstrap_roles_users.py --environment production
  python3 scripts/bootstrap_roles_users.py --dry-run --verbose
  python3 scripts/bootstrap_roles_users.py --environment production --verbose
        """
    )
    parser.add_argument(
        "--environment",
        choices=["development", "production"],
        default="development",
        help="Target environment (default: development)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )
    parser.add_argument(
        "--log-file",
        default="bootstrap_debug.log",
        help="Log file path (default: bootstrap_debug.log)"
    )
    
    args = parser.parse_args()
    
    # Configure logging level based on arguments
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Verbose logging enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Update log file handler
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logging.getLogger().removeHandler(handler)
    
    file_handler = logging.FileHandler(args.log_file, mode='w')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    ))
    logging.getLogger().addHandler(file_handler)
    
    logger.info("🚀 MOROCCAN TOURIST TRANSPORT ERP - BOOTSTRAP SCRIPT")
    logger.info("=" * 60)
    logger.info(f"📅 Start time: {datetime.utcnow().isoformat()}")
    logger.info(f"🔧 Environment: {args.environment}")
    logger.info(f"🔍 Dry run: {args.dry_run}")
    logger.info(f"📝 Verbose: {args.verbose}")
    logger.info(f"📄 Log file: {args.log_file}")
    logger.info(f"🐍 Python version: {sys.version}")
    logger.info(f"📂 Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    if args.dry_run:
        logger.info("🔍 Running in DRY RUN mode - no changes will be made")
        logger.info("📋 This will show you exactly what would be created")
    
    # Log system information
    logger.debug("🖥️ System information:")
    logger.debug(f"   - Platform: {sys.platform}")
    logger.debug(f"   - Python executable: {sys.executable}")
    logger.debug(f"   - Script path: {__file__}")
    
    # Log environment variables (without sensitive data)
    logger.debug("🌍 Environment variables:")
    env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'PYTHONPATH']
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        logger.debug(f"   - {var}: {value}")
    
    # Initialize database connection
    logger.info("🔌 Initializing database connection...")
    db_connection = DatabaseConnection(args.environment)
    
    try:
        # Test database connection first
        logger.info("🧪 Testing database connection...")
        test_conn = db_connection.connect()
        logger.info("✅ Database connection test successful")
        
        # Initialize bootstrap process
        logger.info("🔧 Initializing bootstrap process...")
        bootstrap = RoleUserBootstrap(db_connection, dry_run=args.dry_run)
        
        # Log what will be processed
        logger.info(f"📊 Bootstrap scope:")
        logger.info(f"   - Roles to process: {len(ROLE_DEFINITIONS)}")
        logger.info(f"   - Users to process: {len(DEMO_USERS)}")
        logger.info(f"   - Total permissions defined: {sum(len(role.get('permissions', [])) for role in ROLE_DEFINITIONS.values())}")
        
        # Run bootstrap
        logger.info("🎯 Starting bootstrap execution...")
        bootstrap.run_bootstrap()
        
        logger.info("🎉 Bootstrap script completed successfully!")
        logger.info(f"📄 Detailed logs written to: {args.log_file}")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Bootstrap process interrupted by user (Ctrl+C)")
        logger.info("🔄 You can safely run the script again - it's idempotent")
        sys.exit(1)
    except psycopg2.Error as e:
        logger.error(f"❌ Database error: {e}")
        logger.debug(f"🔍 Database error details:", exc_info=True)
        logger.info("💡 Troubleshooting tips:")
        logger.info("   - Check if PostgreSQL is running")
        logger.info("   - Verify database connection parameters")
        logger.info("   - Ensure database exists and user has permissions")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Bootstrap process failed: {e}")
        logger.debug(f"🔍 Exception details:", exc_info=True)
        logger.info("💡 Check the detailed logs for more information")
        sys.exit(1)
    finally:
        logger.info("🔌 Closing database connection...")
        db_connection.close()
        logger.info("👋 Bootstrap script finished")


if __name__ == "__main__":
    main()

