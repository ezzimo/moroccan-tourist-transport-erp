#!/usr/bin/env python3
"""
Script to create a test user directly in the database
"""
import hashlib
import os
import uuid
from datetime import datetime
import psycopg2
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_test_user():
    # User data
    user_id = str(uuid.uuid4())
    full_name = "Ahmed Hassan"
    email = "ahmed@example.com"
    phone = "+212600123456"
    password = "SecurePassword123!"
    password_hash = hash_password(password)
    created_at = datetime.utcnow()
    
    # Default values for not-null columns
    is_active = True
    is_verified = True
    is_locked = False  # ✅ PATCH
    must_change_password = False  # ✅ PATCH
    failed_login_attempts = 0  # ✅ PATCH

    # Database connection
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "db_auth"),
        port="5432",
        database="auth_db",
        user="postgres",
        password="password"
    )
    
    try:
        cursor = conn.cursor()
        
        # Insert user
        insert_query = """
        INSERT INTO users (
            id, full_name, email, phone, password_hash,
            is_active, is_verified, is_locked,
            must_change_password, failed_login_attempts, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            user_id, full_name, email, phone, password_hash,
            is_active, is_verified, is_locked,
            must_change_password, failed_login_attempts, created_at
        ))
        
        conn.commit()
        print(f"✅ Test user created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔐 Password: {password}")
        print(f"🆔 User ID: {user_id}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_test_user()
