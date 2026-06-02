# Property Tax Management System (PTMS)
## Complete Setup & Developer Guide

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Requirements](#2-system-requirements)
3. [Project File Structure](#3-project-file-structure)
4. [Database Design](#4-database-design)
5. [Frontend Design](#5-frontend-design)
6. [Installation & Setup](#6-installation--setup)
7. [Running the Application](#7-running-the-application)
8. [Database Objects Reference](#8-database-objects-reference)
9. [SQL Query Categories](#9-sql-query-categories)
10. [Default Credentials](#10-default-credentials)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Project Overview

**Property Tax Management System (PTMS)** is a desktop application built for Municipal Corporations to manage property tax assessment, collection, dues tracking, and reporting.

### Key Features
- Property registration with owner and ward linkage
- Automated tax calculation by property type (SP: `sp_calculate_tax`)
- Payment recording with auto-status update (Trigger: `trg_after_payment_update_status`)
- Penalty application for overdue records (SP: `sp_apply_penalty`)
- Reports: Defaulters list, Ward-wise collection, Annual revenue
- Role-based access: Admin, Clerk, Viewer

### Tech Stack
| Layer    | Technology            |
|----------|-----------------------|
| Database | MySQL 8.x             |
| Frontend | Python 3.10+ / Tkinter|
| Driver   | mysql-connector-python|

---

## 2. System Requirements

| Component | Minimum Version |
|-----------|----------------|
| MySQL Server | 8.0+ |
| Python | 3.10+ |admin
| Operating System | Windows 10/11, Ubuntu 20.04+, macOS 12+ |
| RAM | 4 GB |
| Disk Space | 200 MB |

---

## 3. Project File Structure

```
property_tax_mgmt/
│
├── database/
│   ├── 01_schema.sql              ← DDL: all CREATE TABLE statements
│   ├── 02_sample_data.sql         ← DML: 5-10 rows per table
│   ├── 03_views_indexes.sql       ← 5 views + 7 indexes
│   ├── 04_triggers_procedures.sql ← 5 SPs + 5 triggers
│   └── 05_queries.sql             ← DDL, DML, DQL, JOINs, GROUP BY, subqueries
│
├── frontend/
│   ├── main.py          ← Entry point – Login screen
│   ├── dashboard.py     ← Main dashboard with sidebar navigation
│   ├── forms.py         ← All data-entry dialogs
│   ├── db_config.py     ← MySQL connection helper
│   └── requirements.txt ← Python dependencies
│
└── README.md            ← This file
```

---

## 4. Database Design

### Tables Overview

| # | Table Name  | Purpose                          | Rows |
|---|-------------|----------------------------------|------|
| 1 | `ward`      | Municipal ward/area details      | 7    |
| 2 | `owner`     | Property owner KYC details       | 10   |
| 3 | `property`  | Property registry                | 10   |
| 4 | `tax_record`| Annual tax demand per property   | 10   |
| 5 | `payment`   | Payment transactions             | 6    |
| 6 | `users`     | Application login users          | 5    |

---

### Table 1: `ward`

| Field         | Datatype      | Constraints                  |
|---------------|---------------|------------------------------|
| ward_id       | INT           | PK, AUTO_INCREMENT, NOT NULL |
| ward_name     | VARCHAR(100)  | NOT NULL                     |
| ward_number   | VARCHAR(20)   | NOT NULL, UNIQUE             |
| zone          | VARCHAR(50)   | NOT NULL                     |
| officer_name  | VARCHAR(100)  | NOT NULL                     |
| contact_email | VARCHAR(150)  | NOT NULL                     |
| created_at    | DATETIME      | NOT NULL, DEFAULT NOW()      |

---

### Table 2: `owner`

| Field         | Datatype      | Constraints                        |
|---------------|---------------|------------------------------------|
| owner_id      | INT           | PK, AUTO_INCREMENT, NOT NULL       |
| first_name    | VARCHAR(80)   | NOT NULL                           |
| last_name     | VARCHAR(80)   | NOT NULL                           |
| email         | VARCHAR(150)  | NOT NULL, UNIQUE                   |
| phone         | VARCHAR(15)   | NOT NULL, CHECK(len >= 10)         |
| address       | VARCHAR(255)  | NOT NULL                           |
| aadhar_number | CHAR(12)      | NOT NULL, UNIQUE, CHECK(len == 12) |
| pan_number    | VARCHAR(10)   | UNIQUE, NULLABLE                   |
| created_at    | DATETIME      | NOT NULL, DEFAULT NOW()            |

---

### Table 3: `property`

| Field             | Datatype         | Constraints                           |
|-------------------|------------------|---------------------------------------|
| property_id       | INT              | PK, AUTO_INCREMENT, NOT NULL          |
| property_number   | VARCHAR(30)      | NOT NULL, UNIQUE                      |
| owner_id          | INT              | NOT NULL, FK → owner(owner_id)        |
| ward_id           | INT              | NOT NULL, FK → ward(ward_id)          |
| address           | VARCHAR(255)     | NOT NULL                              |
| property_type     | ENUM             | Residential/Commercial/Industrial/Agricultural |
| area_sqft         | DECIMAL(10,2)    | NOT NULL, CHECK(> 0)                  |
| floors            | TINYINT UNSIGNED | NOT NULL, DEFAULT 1                   |
| construction_year | YEAR             | NOT NULL                              |
| annual_value      | DECIMAL(15,2)    | NOT NULL, CHECK(>= 0)                 |
| is_active         | TINYINT(1)       | NOT NULL, DEFAULT 1                   |
| registered_at     | DATETIME         | NOT NULL, DEFAULT NOW()               |

---

### Table 4: `tax_record`

| Field          | Datatype       | Constraints                                         |
|----------------|----------------|-----------------------------------------------------|
| tax_id         | INT            | PK, AUTO_INCREMENT, NOT NULL                        |
| property_id    | INT            | NOT NULL, FK → property(property_id)                |
| financial_year | VARCHAR(9)     | NOT NULL (e.g. '2024-2025')                         |
| tax_amount     | DECIMAL(12,2)  | NOT NULL, CHECK(>= 0)                               |
| penalty_amount | DECIMAL(12,2)  | NOT NULL, DEFAULT 0, CHECK(>= 0)                    |
| rebate_amount  | DECIMAL(12,2)  | NOT NULL, DEFAULT 0, CHECK(>= 0)                    |
| total_due      | DECIMAL(12,2)  | NOT NULL (auto-computed by trigger)                 |
| due_date       | DATE           | NOT NULL                                            |
| status         | ENUM           | Pending/Partial/Paid/Overdue/Waived, DEFAULT Pending|
| generated_at   | DATETIME       | NOT NULL, DEFAULT NOW()                             |
| updated_at     | DATETIME       | NOT NULL, ON UPDATE CURRENT_TIMESTAMP               |
| (UK)           |                | UNIQUE (property_id, financial_year)                |

---

### Table 5: `payment`

| Field           | Datatype       | Constraints                          |
|-----------------|----------------|--------------------------------------|
| payment_id      | INT            | PK, AUTO_INCREMENT, NOT NULL         |
| tax_id          | INT            | NOT NULL, FK → tax_record(tax_id)    |
| amount_paid     | DECIMAL(12,2)  | NOT NULL, CHECK(> 0)                 |
| payment_date    | DATETIME       | NOT NULL, DEFAULT NOW()              |
| payment_mode    | ENUM           | Cash/Cheque/Online/DD/NEFT/UPI       |
| transaction_ref | VARCHAR(100)   | UNIQUE, NULLABLE                     |
| receipt_number  | VARCHAR(30)    | NOT NULL, UNIQUE                     |
| remarks         | VARCHAR(255)   | NULLABLE                             |

---

### Table 6: `users`

| Field         | Datatype       | Constraints                          |
|---------------|----------------|--------------------------------------|
| user_id       | INT            | PK, AUTO_INCREMENT, NOT NULL         |
| username      | VARCHAR(60)    | NOT NULL, UNIQUE                     |
| password_hash | VARCHAR(255)   | NOT NULL (SHA-256)                   |
| role          | ENUM           | admin/clerk/viewer, DEFAULT viewer   |
| full_name     | VARCHAR(150)   | NOT NULL                             |
| email         | VARCHAR(150)   | NOT NULL, UNIQUE                     |
| is_active     | TINYINT(1)     | NOT NULL, DEFAULT 1                  |
| last_login    | DATETIME       | NULLABLE                             |
| created_at    | DATETIME       | NOT NULL, DEFAULT NOW()              |

---

### Entity Relationship Summary

```
ward (1) ──────< property (M)
owner (1) ──────< property (M)
property (1) ──────< tax_record (M)
tax_record (1) ──────< payment (M)
```

---

## 5. Frontend Design

### User Interface Design

The frontend uses **Tkinter** with a custom clean light theme.

**Colour Palette:**
| Name         | Hex       | Usage              |
|--------------|-----------|--------------------|
| Background   | `#f8fafc` | Window base        |
| Card         | `#ffffff` | Form cards         |
| Field        | `#f1f5f9` | Input backgrounds  |
| Sidebar      | `#f1f5f9` | Sidebar background |
| Accent Gold  | `#d97706` | Headings, buttons  |
| Accent Green | `#059669` | Success states     |
| Danger Red   | `#ef4444` | Errors, overdue    |
| Text Light   | `#1e293b` | Main body text     |
| Text Muted   | `#64748b` | Labels, hints      |

**Fonts:** Georgia (headings), Segoe UI (body)

---

### Forms & Pages Used

| Form/Page            | File         | Purpose                           |
|----------------------|--------------|-----------------------------------|
| Login Form           | main.py      | Username/password authentication  |
| Dashboard            | dashboard.py | KPI cards + quick navigation      |
| Wards Page           | dashboard.py | List and manage registered wards  |
| Property Form/Page   | forms.py/dash| Register & list properties        |
| Owner Form/Page      | forms.py/dash| Register & list owners            |
| Tax Generate Form    | forms.py     | Call sp_calculate_tax             |
| Payment Form         | forms.py     | Call sp_record_payment            |
| User Form            | forms.py     | Admin: create system users        |
| Ward Form            | forms.py     | Admin/Clerk: add wards            |

---

### Navigation Flow

```
[Login Page]
     │
     ▼ (successful auth)
[Dashboard]
     │
     ├── 🏙 Wards ────────► [Ward List]     ──► [Add Ward Form]
     ├── 🏘 Properties ──► [Property List] ──► [Add Property Form]
     ├── 👤 Owners ───────► [Owner List]   ──► [Add Owner Form]
     ├── 🗂 Tax Records ──► [Tax List]     ──► [Generate Tax Form]
     │                                     ──► [Apply Penalties]
     ├── 💳 Payments ─────► [Payment List] ──► [Record Payment Form]
     ├── 📊 Reports ──────► [Defaulters Tab]
     │                  ──► [Ward Collection Tab]
     │                  ──► [Annual Revenue Tab]
     └── 🔧 Admin Panel ──► [User Management]
                        ──► [Wards Navigation Link]
                        ──► [Run Tax Calc]
```

---

### Example Screens

#### Login Page
- Full-screen centred light card
- Username + password fields with show/hide toggle
- DB connectivity warning if MySQL is unreachable
- Default credentials shown in footer

#### Dashboard
- Left sidebar: navigation menu with role-gated items
- Top: 4 KPI cards (Properties, Collected, Defaulters, Overdue)
- Bottom: Recent payments table (last 10)

#### Registration Form
- Light card dialog (modal) with thin gold border
- Labelled entry fields on light gray background with gold accent
- Required field markers (*)
- Inline status/error messages
- Save / Cancel buttons

#### Report Page
- Tabbed notebook: Defaulters | Ward Collection | Annual Revenue
- Sortable treeview tables
- Data sourced from database views

---

## 6. Installation & Setup

### Step 1: Install MySQL Server

**Windows:**
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run installer, select "Server only" or "Full"
3. Set root password during setup
4. Start MySQL service (should start automatically)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

---

### Step 2: Install Python 3.10+

**Windows:**
1. Download from https://www.python.org/downloads/
2. ✅ Check "Add Python to PATH" during installation

**Ubuntu:**
```bash
sudo apt install python3 python3-pip python3-tk -y
```

**macOS:**
```bash
brew install python-tk
```

> **Important for Ubuntu/macOS:** Tkinter must be installed separately.
> Ubuntu: `sudo apt install python3-tk`
> macOS: `brew install python-tk`

---

### Step 3: Clone / Extract the Project

```bash
# If using git:
git clone <repo-url>

# Or extract the zip:
unzip property_tax_mgmt.zip
cd property_tax_mgmt
```

---

### Step 4: Install Python Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

> On some systems use `pip3` instead of `pip`.

---

### Step 5: Configure Database Credentials

Open `frontend/db_config.py` and update:

```python
DB_HOST     = "localhost"     # MySQL host
DB_PORT     = 3306            # MySQL port (default 3306)
DB_NAME     = "property_tax_db"
DB_USER     = "root"          # Your MySQL username
DB_PASSWORD = "YOUR_PASSWORD" # ← CHANGE THIS
```

---

### Step 6: Run SQL Scripts in Order

Connect to MySQL:

```bash
mysql -u root -p
```

Then run the scripts **in this exact order**:

```sql
SOURCE /path/to/database/01_schema.sql;
SOURCE /path/to/database/02_sample_data.sql;
SOURCE /path/to/database/03_views_indexes.sql;
SOURCE /path/to/database/04_triggers_procedures.sql;
SOURCE /path/to/database/05_queries.sql;
```

**Or use MySQL Workbench:**
1. Open MySQL Workbench
2. Connect to your server
3. File → Open SQL Script → select each file
4. Run them in order (01 → 02 → 03 → 04 → 05)

**Or use the command line (recommended):**
```bash
mysql -u root -p < database/01_schema.sql
mysql -u root -p < database/02_sample_data.sql
mysql -u root -p < database/03_views_indexes.sql
mysql -u root -p < database/04_triggers_procedures.sql
mysql -u root -p < database/05_queries.sql
```

---

### Step 7: Verify Database Setup

```sql
USE property_tax_db;
SHOW TABLES;
SELECT COUNT(*) FROM property;   -- should return 10
SELECT COUNT(*) FROM owner;      -- should return 10
SELECT COUNT(*) FROM payment;    -- should return 6
SHOW PROCEDURE STATUS WHERE Db = 'property_tax_db';
SHOW TRIGGERS FROM property_tax_db;
```

---

## 7. Running the Application

```bash
cd frontend
python main.py
```

> On Linux/macOS: `python3 main.py`

The login window will appear. Use the credentials below.

---

## 8. Database Objects Reference

### Views

| View Name                  | Description                              |
|---------------------------|------------------------------------------|
| `v_property_tax_summary`  | Full join: property + owner + ward + tax |
| `v_defaulters`            | Overdue/Pending records with days overdue|
| `v_ward_collection_summary`| Ward-wise demand vs collected           |
| `v_payment_history`       | Full payment history with property/owner |
| `v_annual_revenue`        | Year-wise revenue totals                 |

### Indexes

| Index Name                | Table        | Column(s)            |
|---------------------------|--------------|----------------------|
| `idx_property_owner_id`   | property     | owner_id             |
| `idx_property_ward_id`    | property     | ward_id              |
| `idx_tax_status`          | tax_record   | status               |
| `idx_tax_financial_year`  | tax_record   | financial_year       |
| `idx_payment_date`        | payment      | payment_date         |
| `idx_payment_tax_id`      | payment      | tax_id               |
| `idx_owner_name`          | owner        | last_name, first_name|
| `idx_status_due`          | tax_record   | status, due_date     |

### Stored Procedures

| Procedure              | Parameters                          | Description                          |
|------------------------|-------------------------------------|--------------------------------------|
| `sp_calculate_tax`     | IN: property_id, fy, due_date; OUT: tax_id, message | Calculate & insert/update tax record |
| `sp_record_payment`    | IN: tax_id, amount, mode, ref; OUT: receipt, message | Record payment, update status       |
| `sp_apply_penalty`     | OUT: records_updated, message       | Apply 10% penalty to overdue records |
| `sp_get_defaulters_report` | IN: ward_id (NULL=all)          | List all defaulters (optionally by ward) |
| `sp_ward_collection_report` | IN: financial_year             | Ward-wise collection for a given FY  |

### Triggers

| Trigger Name                          | Event              | Table        | Action                                      |
|---------------------------------------|--------------------|--------------|---------------------------------------------|
| `trg_after_payment_update_status`     | AFTER INSERT       | payment      | Recalculate and update tax_record status    |
| `trg_before_tax_record_insert`        | BEFORE INSERT      | tax_record   | Auto-compute total_due                      |
| `trg_before_tax_record_update`        | BEFORE UPDATE      | tax_record   | Recalculate total_due on any field change   |
| `trg_after_property_annual_value_change` | AFTER UPDATE    | property     | Propagate annual_value change to tax record |
| `trg_before_payment_delete`           | BEFORE DELETE      | payment      | Block deletion of payment for Paid records  |

---

## 9. SQL Query Categories

All queries are in `database/05_queries.sql`:

| Category  | Examples                                                        |
|-----------|-----------------------------------------------------------------|
| DDL       | ALTER TABLE (add columns, add index)                            |
| DML       | UPDATE owner phone, bulk rebate update, mark overdue            |
| DQL       | SELECT with JOINs, filters, ORDER BY                            |
| JOIN      | INNER JOIN, LEFT JOIN, multi-table JOIN (5 tables)              |
| GROUP BY  | Ward-wise, annual revenue, payment mode distribution            |
| Subquery  | Properties above avg tax, owners who never paid, top ward       |
| HAVING    | Wards with overdue count > 0                                    |

### Tax Rate Table

| Property Type | Tax Rate |
|---------------|----------|
| Residential   | 2.00%    |
| Commercial    | 3.00%    |
| Industrial    | 4.00%    |
| Agricultural  | 0.50%    |

---

## 10. Default Credentials

| Username | Password   | Role   | Access                        |
|----------|------------|--------|-------------------------------|
| admin    | admin123  | Admin  | Full access + admin panel     |
| clerk1   | Clerk@123  | Clerk  | Add/edit properties, payments |
| clerk2   | Clerk@456  | Clerk  | Add/edit properties, payments |
| viewer1  | View@123   | Viewer | Read-only access              |
| viewer2  | View@456   | Viewer | Read-only access              |

> Passwords are stored as SHA-256 hashes. Change them after first login via the Admin Panel.

---

## 11. Troubleshooting

### "Can't connect to MySQL server"
- Ensure MySQL service is running:
  - Windows: Services → MySQL80 → Start
  - Linux: `sudo systemctl start mysql`
  - macOS: `brew services start mysql`
- Verify credentials in `db_config.py`
- Try: `mysql -u root -p` in terminal to test manually

### "ModuleNotFoundError: No module named 'mysql'"
```bash
pip install mysql-connector-python
```

### "ModuleNotFoundError: No module named 'tkinter'"
- Ubuntu: `sudo apt install python3-tk`
- macOS: `brew install python-tk@3.11` (match your Python version)
- Windows: Reinstall Python with "tcl/tk and IDLE" option checked

### "Stored procedure does not exist"
- Ensure you ran `04_triggers_procedures.sql` after `01_schema.sql`
- Check: `SHOW PROCEDURE STATUS WHERE Db='property_tax_db';`

### "Access denied for user 'root'"
- Use a non-root MySQL user:
  ```sql
  CREATE USER 'ptms_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
  GRANT ALL PRIVILEGES ON property_tax_db.* TO 'ptms_user'@'localhost';
  FLUSH PRIVILEGES;
  ```
  Then update `db_config.py` with `DB_USER='ptms_user'` and `DB_PASSWORD='StrongPass123!'`

### Application window appears blank / small
- Increase display scaling or set a larger default geometry in `main.py`

---

## License

This project is developed for academic/educational purposes as part of a DBMS mini project.

---

*Property Tax Management System – DBMS Mini Project*
*Stack: MySQL 8.x + Python 3.10+ / Tkinter*
