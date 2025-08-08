Based on your architecture, service modules, and targeted sectors (Ground, Tourist, Corporate Shuttle, and Employee Transportation), here is a comprehensive list of **user types** and **role types** for your ERP system:

---

## 👥 USER TYPES (High-Level Categories)

| User Type                 | Description                                                                 |
| ------------------------- | --------------------------------------------------------------------------- |
| **System Super Admin**    | Manages tenants, system configs, master data, and compliance across clients |
| **Company Admin**         | Administers a single company’s ERP account, roles, and configurations       |
| **Operations Staff**      | Manages routes, bookings, dispatch, and schedules                           |
| **Fleet Manager**         | Oversees vehicles, fuel, maintenance, documentation                         |
| **Driver**                | Mobile app user handling assigned trips, navigation, incidents              |
| **HR Staff**              | Handles recruitment, employee files, training, and documents                |
| **Finance Staff**         | Manages billing, invoices, payments, reports, tax compliance                |
| **Inventory Manager**     | Oversees stock, supplies, and supplier orders                               |
| **QA & Compliance Agent** | Manages audits, certifications, and non-conformities                        |
| **Customer Support**      | Responds to client inquiries, complaints, and feedback                      |
| **Corporate Client**      | Company (B2B) client booking shuttles or employee transport                 |
| **Retail Client**         | Individual or small group booking transport or tours                        |
| **Partner Supplier**      | Provides vehicle parts, fuel, or subcontracted transport                    |

---

## 🔐 ROLE TYPES (With Granular Access Control)

### 🛠️ **Administration Roles**

| Role           | Permissions                                           |
| -------------- | ----------------------------------------------------- |
| `super_admin`  | Full access to all tenant data, settings, audit logs  |
| `tenant_admin` | Full control of a company's instance, users, services |
| `role_manager` | Can create/edit roles and assign permissions          |

---

### 🚍 **Operational Roles**

| Role                     | Permissions                                          |
| ------------------------ | ---------------------------------------------------- |
| `dispatcher`             | Manage bookings, routes, driver assignments          |
| `route_planner`          | Create/edit route templates, scheduling              |
| `booking_manager`        | Approve/reschedule/cancel reservations               |
| `client_account_manager` | Handle key clients, contract terms, special requests |

---

### 🚐 **Fleet Roles**

| Role               | Permissions                                |
| ------------------ | ------------------------------------------ |
| `fleet_manager`    | Manage vehicles, assignments, compliance   |
| `maintenance_tech` | View/update maintenance records, schedules |
| `fuel_log_manager` | Log fuel usage, monitor efficiency         |

---

### 👨‍✈️ **Driver Roles**

| Role          | Permissions                                            |
| ------------- | ------------------------------------------------------ |
| `driver`      | Mobile app: see tasks, upload documents, report issues |
| `lead_driver` | Driver + ability to supervise/co-sign incidents        |

---

### 👥 **HR & Staff Roles**

| Role         | Permissions                                   |
| ------------ | --------------------------------------------- |
| `hr_manager` | Manage employees, contracts, leaves, training |
| `recruiter`  | Post jobs, manage applications                |
| `trainer`    | Assign and track driver/staff training        |

---

### 💰 **Finance Roles**

| Role              | Permissions                                    |
| ----------------- | ---------------------------------------------- |
| `finance_manager` | Full access to invoices, expenses, tax reports |
| `billing_agent`   | Issue invoices, track payments                 |
| `accountant`      | View ledgers, manage financial reports         |

---

### 🛒 **Inventory Roles**

| Role                | Permissions                              |
| ------------------- | ---------------------------------------- |
| `inventory_manager` | Manage items, suppliers, purchase orders |
| `warehouse_staff`   | Record movements, confirm deliveries     |

---

### 📋 **QA & Compliance Roles**

| Role                 | Permissions                                              |
| -------------------- | -------------------------------------------------------- |
| `qa_officer`         | Run audits, manage non-conformities                      |
| `compliance_officer` | Track certifications, vehicle/driver document compliance |

---

### 📞 **Customer & Client Roles**

| Role                     | Permissions                             |
| ------------------------ | --------------------------------------- |
| `corporate_client_admin` | Book/manage trips for company employees |
| `client_user`            | View trips, invoices, submit feedback   |
| `individual_customer`    | Create personal bookings, rate services |

---

### 📣 **Notification & Communication**

| Role                    | Permissions                                       |
| ----------------------- | ------------------------------------------------- |
| `communication_manager` | Create/manage notification templates, campaigns   |
| `alert_dispatcher`      | Trigger real-time messages (delays, issues, etc.) |

---

## 🧩 RBAC Hierarchy (Example)

```txt
super_admin
├── tenant_admin
│   ├── dispatcher
│   ├── fleet_manager
│   ├── hr_manager
│   ├── finance_manager
│   ├── inventory_manager
│   └── qa_officer
└── client_user / driver / partner_supplier (lowest privilege)
```

---

## ✅ Next Step

Perfect. Here's the full expert deliverable broken into the **3 required parts**:

---

# ✅ 1. Role → API Permissions Mapping

This table summarizes **which API operations** each role can access, organized by **ERP microservice**:

| Microservice           | Endpoint Domain                                                    | Roles with Access                                                                        |
| ---------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `auth_service`         | `/auth`, `/users`, `/roles`                                        | `super_admin`, `tenant_admin`, `role_manager`                                            |
| `crm_service`          | `/customers`, `/feedback`                                          | `client_account_manager`, `tenant_admin`, `crm_agent`, `customer_support`                |
| `fleet_service`        | `/vehicles`, `/maintenance`, `/fuel`, `/assignments`               | `fleet_manager`, `maintenance_tech`, `fuel_log_manager`, `tenant_admin`                  |
| `driver_service`       | `/drivers`, `/assignments`, `/training`, `/incidents`              | `driver`, `lead_driver`, `driver_trainer`, `dispatcher`, `tenant_admin`                  |
| `booking_service`      | `/bookings`, `/reservations`, `/availability`, `/pricing`          | `dispatcher`, `booking_manager`, `client_user`, `corporate_client_admin`, `tenant_admin` |
| `route_service`        | `/routes`, `/planning`                                             | `route_planner`, `dispatcher`, `tenant_admin`                                            |
| `financial_service`    | `/invoices`, `/payments`, `/expenses`, `/tax-reports`              | `finance_manager`, `billing_agent`, `accountant`, `tenant_admin`                         |
| `inventory_service`    | `/items`, `/suppliers`, `/stock`, `/purchase-orders`               | `inventory_manager`, `warehouse_staff`, `tenant_admin`                                   |
| `hr_service`           | `/employees`, `/recruitment`, `/training`                          | `hr_manager`, `recruiter`, `trainer`, `tenant_admin`                                     |
| `notification_service` | `/notifications`, `/templates`, `/logs`                            | `communication_manager`, `alert_dispatcher`, `tenant_admin`                              |
| `qa_service`           | `/audits`, `/compliance`, `/certifications`, `/nonconformities`    | `qa_officer`, `compliance_officer`, `tenant_admin`                                       |
| `tour_service`         | `/tour-templates`, `/tour-instances`, `/itineraries`, `/incidents` | `tour_manager`, `dispatcher`, `tenant_admin`                                             |

---

# 🌐 2. Role Labels (i18n: English / French / Arabic)

| `role_key`               | English Label          | French Label                   | Arabic Label         |
| ------------------------ | ---------------------- | ------------------------------ | -------------------- |
| `super_admin`            | System Super Admin     | Super Administrateur Système   | المشرف العام للنظام  |
| `tenant_admin`           | Company Admin          | Administrateur de l'entreprise | مشرف الشركة          |
| `role_manager`           | Role Manager           | Gestionnaire des rôles         | مدير الصلاحيات       |
| `dispatcher`             | Dispatcher             | Dispatcheur                    | مسؤول الجدولة        |
| `route_planner`          | Route Planner          | Planificateur des trajets      | مخطط المسارات        |
| `booking_manager`        | Booking Manager        | Responsable des réservations   | مدير الحجوزات        |
| `client_account_manager` | Client Account Manager | Gestionnaire de comptes client | مدير حسابات العملاء  |
| `fleet_manager`          | Fleet Manager          | Gestionnaire de flotte         | مدير الأسطول         |
| `maintenance_tech`       | Maintenance Technician | Technicien de maintenance      | فني الصيانة          |
| `fuel_log_manager`       | Fuel Log Manager       | Responsable carburant          | مسؤول سجلات الوقود   |
| `driver`                 | Driver                 | Chauffeur                      | السائق               |
| `lead_driver`            | Lead Driver            | Chef Chauffeur                 | السائق الرئيسي       |
| `hr_manager`             | HR Manager             | Responsable RH                 | مدير الموارد البشرية |
| `recruiter`              | Recruiter              | Recruteur                      | مسؤول التوظيف        |
| `trainer`                | Trainer                | Formateur                      | المدرب               |
| `finance_manager`        | Finance Manager        | Responsable financier          | المدير المالي        |
| `billing_agent`          | Billing Agent          | Agent de facturation           | مسؤول الفوترة        |
| `accountant`             | Accountant             | Comptable                      | محاسب                |
| `inventory_manager`      | Inventory Manager      | Responsable des stocks         | مدير المخزون         |
| `warehouse_staff`        | Warehouse Staff        | Magasinier                     | موظف المستودع        |
| `qa_officer`             | QA Officer             | Agent qualité                  | مسؤول الجودة         |
| `compliance_officer`     | Compliance Officer     | Agent conformité               | مسؤول المطابقة       |
| `client_user`            | Individual Client      | Client Individuel              | عميل فردي            |
| `corporate_client_admin` | Corporate Client Admin | Admin Client Entreprise        | مدير عميل مؤسسي      |
| `communication_manager`  | Communication Manager  | Responsable communication      | مسؤول التواصل        |
| `alert_dispatcher`       | Alert Dispatcher       | Envoyeur d’alertes             | مرسل التنبيهات       |

---

# 🔐 3. Default Permissions Per Microservice (Granular)

Each microservice can use **role-based access control** like so:

## 📦 `fleet_service`

| Role               | Permissions                                    |
| ------------------ | ---------------------------------------------- |
| `fleet_manager`    | full CRUD on vehicles, docs, fuel, maintenance |
| `maintenance_tech` | read/update maintenance records                |
| `fuel_log_manager` | create/view fuel logs                          |

---

## 📦 `driver_service`

| Role          | Permissions                              |
| ------------- | ---------------------------------------- |
| `driver`      | read own profile, upload documents       |
| `lead_driver` | all driver permissions + incident report |
| `dispatcher`  | assign drivers to routes                 |

---

## 📦 `booking_service`

| Role                     | Permissions                |
| ------------------------ | -------------------------- |
| `booking_manager`        | full CRUD bookings         |
| `dispatcher`             | assign drivers to bookings |
| `corporate_client_admin` | create/view bookings       |
| `client_user`            | create/view own bookings   |

---

## 📦 `financial_service`

| Role              | Permissions                        |
| ----------------- | ---------------------------------- |
| `finance_manager` | all finance data (invoices, taxes) |
| `billing_agent`   | create/view invoices, payments     |
| `accountant`      | view financial reports             |

---

## 📦 `hr_service`

| Role         | Permissions                  |
| ------------ | ---------------------------- |
| `hr_manager` | full employee CRUD           |
| `recruiter`  | create/view job applications |
| `trainer`    | manage training programs     |

---

## 📦 `inventory_service`

| Role                | Permissions                        |
| ------------------- | ---------------------------------- |
| `inventory_manager` | manage items, suppliers            |
| `warehouse_staff`   | view items, record stock movements |

---

## 📦 `notification_service`

| Role                    | Permissions                    |
| ----------------------- | ------------------------------ |
| `communication_manager` | manage templates, campaigns    |
| `alert_dispatcher`      | send SMS/email/WhatsApp alerts |

---

## 📦 `qa_service`

| Role                 | Permissions                        |
| -------------------- | ---------------------------------- |
| `qa_officer`         | run audits, manage results         |
| `compliance_officer` | ensure document/vehicle compliance |

---

## 📦 `crm_service`

| Role                     | Permissions                 |
| ------------------------ | --------------------------- |
| `client_account_manager` | manage corporate clients    |
| `customer_support`       | handle feedback, complaints |

---

## 📦 `tour_service`

| Role           | Permissions                      |
| -------------- | -------------------------------- |
| `tour_manager` | manage tour templates, schedules |
| `dispatcher`   | assign vehicles/drivers to tours |

---

### Role Permissions Map→ Permissions JSON Map:
```
{
  "fleet_service": {
    "fleet_manager": ["vehicles:create", "vehicles:read", "vehicles:update", "vehicles:delete", "maintenance:*", "fuel:*"],
    "maintenance_tech": ["maintenance:read", "maintenance:update"],
    "fuel_log_manager": ["fuel:create", "fuel:read"]
  },
  "driver_service": {
    "driver": ["profile:read", "documents:upload"],
    "lead_driver": ["profile:read", "documents:upload", "incidents:create"],
    "dispatcher": ["assignments:create", "assignments:read"]
  },
  "booking_service": {
    "booking_manager": ["bookings:create", "bookings:read", "bookings:update", "bookings:delete"],
    "dispatcher": ["assignments:create", "assignments:read"],
    "corporate_client_admin": ["bookings:create", "bookings:read"],
    "client_user": ["bookings:create", "bookings:read:own"]
  },
  "financial_service": {
    "finance_manager": ["invoices:*", "payments:*", "expenses:*", "tax_reports:*"],
    "billing_agent": ["invoices:create", "invoices:read", "payments:create", "payments:read"],
    "accountant": ["reports:read"]
  },
  "hr_service": {
    "hr_manager": ["employees:*"],
    "recruiter": ["recruitment:create", "recruitment:read"],
    "trainer": ["training:*"]
  },
  "inventory_service": {
    "inventory_manager": ["items:*", "suppliers:*"],
    "warehouse_staff": ["stock_movements:create", "items:read"]
  },
  "notification_service": {
    "communication_manager": ["templates:*", "notifications:*"],
    "alert_dispatcher": ["alerts:send"]
  },
  "qa_service": {
    "qa_officer": ["audits:*", "nonconformities:*"],
    "compliance_officer": ["certifications:*", "compliance:*"]
  },
  "crm_service": {
    "client_account_manager": ["customers:*", "segments:*"],
    "customer_support": ["feedback:*", "interactions:*"]
  },
  "tour_service": {
    "tour_manager": ["tour_templates:*", "tour_instances:*"],
    "dispatcher": ["incidents:*", "assignments:*"]
  }
}
```


