# Bootstrap Scripts Documentation

This directory contains automation scripts for setting up and managing the Moroccan Tourist Transport ERP system.

## 🚀 Bootstrap Roles and Users Script

The `bootstrap_roles_users.py` script automates the creation of roles and demo users for testing and development environments.

### Features

- ✅ **Idempotent**: Safe to run multiple times without duplicating data
- ✅ **Environment-aware**: Supports development and production configurations
- ✅ **Comprehensive role system**: Creates 22 predefined roles with proper permissions
- ✅ **Demo users**: Creates 10 demo users with different role assignments
- ✅ **Dry-run mode**: Preview changes without making modifications
- ✅ **Detailed logging**: Comprehensive output for debugging and monitoring

### Usage

#### Basic Usage

```bash
# Create roles and users for development
python3 scripts/bootstrap_roles_users.py

# Create roles and users for production
python3 scripts/bootstrap_roles_users.py --environment production

# Preview what would be created (dry run)
python3 scripts/bootstrap_roles_users.py --dry-run

# Verbose output for debugging
python3 scripts/bootstrap_roles_users.py --verbose
```

#### Using Makefile

```bash
# Development setup
make bootstrap-users

# Production setup
make bootstrap-users-prod

# Dry run preview
make bootstrap-users-dry

# Complete development environment setup
make dev-setup
```

### Created Roles

The script creates the following role hierarchy:

#### 🛠️ Administration Roles
- `super_admin` - System Super Admin with full access
- `tenant_admin` - Company Admin with full company control
- `role_manager` - Can create/edit roles and permissions

#### 🚍 Operational Roles
- `dispatcher` - Manage bookings, routes, driver assignments
- `route_planner` - Create/edit route templates, scheduling
- `booking_manager` - Approve/reschedule/cancel reservations
- `client_account_manager` - Handle key clients, contracts

#### 🚐 Fleet Roles
- `fleet_manager` - Manage vehicles, assignments, compliance
- `maintenance_tech` - View/update maintenance records
- `fuel_log_manager` - Log fuel usage, monitor efficiency

#### 👨‍✈️ Driver Roles
- `driver` - Mobile app access, upload documents, report issues
- `lead_driver` - Driver permissions + supervise incidents

#### 👥 HR & Staff Roles
- `hr_manager` - Manage employees, contracts, training
- `recruiter` - Post jobs, manage applications
- `trainer` - Assign and track training programs

#### 💰 Finance Roles
- `finance_manager` - Full access to financial data
- `billing_agent` - Issue invoices, track payments
- `accountant` - View ledgers, financial reports

#### 🛒 Inventory Roles
- `inventory_manager` - Manage items, suppliers, orders
- `warehouse_staff` - Record movements, confirm deliveries

#### 📋 QA & Compliance Roles
- `qa_officer` - Run audits, manage non-conformities
- `compliance_officer` - Track certifications, compliance

#### 📞 Customer & Client Roles
- `corporate_client_admin` - Book/manage company trips
- `client_user` - View trips, invoices, submit feedback

#### 📣 Communication Roles
- `communication_manager` - Manage notification templates
- `alert_dispatcher` - Trigger real-time messages

### Created Demo Users

The script creates the following demo users:

| Email | Password | Roles | Description |
|-------|----------|-------|-------------|
| `superadmin@demo.local` | `SuperAdmin123!` | super_admin | System administrator |
| `admin@demo.local` | `Admin123!` | tenant_admin | Company administrator |
| `dispatcher@demo.local` | `Dispatcher123!` | dispatcher | Operations dispatcher |
| `fleetmanager@demo.local` | `Fleet123!` | fleet_manager | Fleet manager |
| `driver@demo.local` | `Driver123!` | driver | Demo driver |
| `hrmanager@demo.local` | `HR123!` | hr_manager | HR manager |
| `financemanager@demo.local` | `Finance123!` | finance_manager | Finance manager |
| `inventorymanager@demo.local` | `Inventory123!` | inventory_manager | Inventory manager |
| `qaofficer@demo.local` | `QA123!` | qa_officer | QA officer |
| `client@demo.local` | `Client123!` | client_user | Demo client |

### Environment Configuration

#### Development Environment
- Database: `localhost:5432/auth_db`
- User: `postgres`
- Password: `password`

#### Production Environment
Uses environment variables:
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

### Integration with CI/CD

#### Docker Integration

Add to your Dockerfile:

```dockerfile
# Copy bootstrap script
COPY scripts/bootstrap_roles_users.py /app/scripts/

# Install dependencies
RUN pip install psycopg2-binary

# Run bootstrap during container startup
RUN python3 scripts/bootstrap_roles_users.py --environment production
```

#### GitHub Actions Integration

```yaml
- name: Bootstrap Roles and Users
  run: |
    python3 scripts/bootstrap_roles_users.py --environment production
  env:
    DB_HOST: ${{ secrets.DB_HOST }}
    DB_USER: ${{ secrets.DB_USER }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

### Error Handling

The script includes comprehensive error handling:

- **Database connection failures**: Clear error messages with connection details
- **Duplicate entries**: Idempotent operations prevent conflicts
- **Missing dependencies**: Helpful installation instructions
- **Permission errors**: Detailed SQL error reporting

### Logging

The script provides detailed logging:

```
2025-07-28 16:20:15,123 - INFO - 🚀 Starting role and user bootstrap process...
2025-07-28 16:20:15,124 - INFO - ✅ Connected to database: auth_db@localhost
2025-07-28 16:20:15,125 - INFO - 🔧 Bootstrapping roles...
2025-07-28 16:20:15,126 - INFO - ✅ Created role: super_admin
2025-07-28 16:20:15,127 - INFO - ✅ Created role: tenant_admin
...
2025-07-28 16:20:15,200 - INFO - 👥 Bootstrapping demo users...
2025-07-28 16:20:15,201 - INFO - ✅ Created user: superadmin@demo.local
...
2025-07-28 16:20:15,300 - INFO - 🎉 Bootstrap process completed successfully!
```

### Security Considerations

- **Password hashing**: Uses bcrypt with proper salt rounds
- **Environment separation**: Different configurations for dev/prod
- **Permission validation**: Proper role-permission mapping
- **SQL injection protection**: Parameterized queries throughout

### Troubleshooting

#### Common Issues

1. **Database connection failed**
   ```bash
   # Check if database is running
   docker ps | grep postgres
   
   # Check connection
   psql -h localhost -U postgres -d auth_db
   ```

2. **Permission denied**
   ```bash
   # Make script executable
   chmod +x scripts/bootstrap_roles_users.py
   ```

3. **Missing dependencies**
   ```bash
   # Install required packages
   pip install sqlmodel passlib psycopg2-binary
   ```

4. **Role already exists**
   - This is normal behavior - the script is idempotent
   - Use `--verbose` flag to see detailed status

### Extending the Script

To add new roles or users:

1. **Add new role to `ROLE_DEFINITIONS`**:
   ```python
   "new_role": {
       "name": "new_role",
       "description": "Description of the new role",
       "permissions": ["service:action", "service:*"],
       "labels": {
           "en": "New Role",
           "fr": "Nouveau Rôle",
           "ar": "دور جديد"
       }
   }
   ```

2. **Add new user to `DEMO_USERS`**:
   ```python
   {
       "email": "newuser@demo.local",
       "full_name": "New User",
       "phone": "+212600000011",
       "password": "NewUser123!",
       "roles": ["new_role"],
       "is_verified": True
   }
   ```

3. **Run the script** to apply changes:
   ```bash
   python3 scripts/bootstrap_roles_users.py
   ```

The script will automatically create only the new roles and users, leaving existing ones unchanged.

