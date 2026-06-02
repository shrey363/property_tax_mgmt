-- ============================================================
--  Property Tax Management System
--  File: 05_queries.sql
--  Description: DDL, DML, DQL, JOINs, GROUP BY, Subqueries
-- ============================================================

USE property_tax_db;

-- ═══════════════════════════════════════════════════════════
--  SECTION A: DDL – ALTER examples
-- ═══════════════════════════════════════════════════════════

-- Add a column to property table
ALTER TABLE property ADD COLUMN latitude  DECIMAL(10,8) DEFAULT NULL;
ALTER TABLE property ADD COLUMN longitude DECIMAL(11,8) DEFAULT NULL;

-- Add index on status + due_date for faster overdue queries
ALTER TABLE tax_record ADD INDEX idx_status_due (status, due_date);

-- ═══════════════════════════════════════════════════════════
--  SECTION B: DML – UPDATE & DELETE examples
-- ═══════════════════════════════════════════════════════════

-- Update owner phone number
UPDATE owner
SET    phone = '9999988888'
WHERE  owner_id = 1;

-- Apply 5% rebate to all Residential properties paid before due date
UPDATE tax_record t
JOIN   property p ON t.property_id = p.property_id
SET    t.rebate_amount = ROUND(t.tax_amount * 0.05, 2)
WHERE  p.property_type = 'Residential'
  AND  t.status        = 'Pending'
  AND  t.due_date      >= CURDATE();

-- Mark old pending records as overdue
UPDATE tax_record
SET    status     = 'Overdue',
       updated_at = NOW()
WHERE  status   = 'Pending'
  AND  due_date < CURDATE();

-- ═══════════════════════════════════════════════════════════
--  SECTION C: DQL – SELECT queries
-- ═══════════════════════════════════════════════════════════

-- 1. All active properties with owner and ward
SELECT
    p.property_number,
    p.address,
    p.property_type,
    p.area_sqft,
    p.annual_value,
    CONCAT(o.first_name, ' ', o.last_name) AS owner,
    w.ward_name
FROM property p
JOIN owner o ON p.owner_id = o.owner_id
JOIN ward  w ON p.ward_id  = w.ward_id
WHERE p.is_active = 1
ORDER BY w.ward_name, p.property_number;

-- 2. Defaulters list (overdue / pending)
SELECT
    p.property_number,
    CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
    o.phone,
    w.ward_name,
    t.financial_year,
    t.total_due,
    t.penalty_amount,
    t.status,
    DATEDIFF(CURDATE(), t.due_date) AS days_overdue
FROM tax_record t
JOIN property p ON t.property_id = p.property_id
JOIN owner    o ON p.owner_id    = o.owner_id
JOIN ward     w ON p.ward_id     = w.ward_id
WHERE t.status IN ('Overdue', 'Pending')
ORDER BY days_overdue DESC;

-- 3. Payment history for a specific property
SELECT
    pay.receipt_number,
    pay.payment_date,
    pay.amount_paid,
    pay.payment_mode,
    t.financial_year,
    t.total_due
FROM payment    pay
JOIN tax_record t ON pay.tax_id = t.tax_id
WHERE t.property_id = 1
ORDER BY pay.payment_date DESC;

-- ═══════════════════════════════════════════════════════════
--  SECTION D: JOIN queries
-- ═══════════════════════════════════════════════════════════

-- 4. INNER JOIN – Properties with tax records this year
SELECT
    p.property_number,
    p.property_type,
    t.financial_year,
    t.tax_amount,
    t.status
FROM property    p
INNER JOIN tax_record t ON p.property_id = t.property_id
WHERE t.financial_year = '2024-2025';

-- 5. LEFT JOIN – All properties even without tax record
SELECT
    p.property_number,
    p.property_type,
    COALESCE(t.financial_year, 'No Record') AS fy,
    COALESCE(t.status, 'Not Generated')     AS tax_status
FROM property    p
LEFT JOIN tax_record t ON p.property_id = t.property_id AND t.financial_year = '2024-2025';

-- 6. Multi-table JOIN – Payment receipt details
SELECT
    pay.receipt_number,
    pay.payment_date,
    pay.amount_paid,
    pay.payment_mode,
    t.financial_year,
    p.property_number,
    p.property_type,
    CONCAT(o.first_name, ' ', o.last_name) AS owner,
    w.ward_name
FROM payment    pay
JOIN tax_record t ON pay.tax_id       = t.tax_id
JOIN property   p ON t.property_id    = p.property_id
JOIN owner      o ON p.owner_id       = o.owner_id
JOIN ward       w ON p.ward_id        = w.ward_id
ORDER BY pay.payment_date DESC;

-- ═══════════════════════════════════════════════════════════
--  SECTION E: GROUP BY queries
-- ═══════════════════════════════════════════════════════════

-- 7. Ward-wise collection summary
SELECT
    w.ward_name,
    w.zone,
    COUNT(DISTINCT p.property_id)               AS total_properties,
    SUM(t.total_due)                            AS total_demand,
    COALESCE(SUM(pay.amount_paid), 0)           AS total_collected,
    SUM(t.total_due) - COALESCE(SUM(pay.amount_paid), 0) AS outstanding
FROM ward        w
LEFT JOIN property   p   ON w.ward_id     = p.ward_id
LEFT JOIN tax_record t   ON p.property_id = t.property_id
LEFT JOIN payment    pay ON t.tax_id      = pay.tax_id
GROUP BY w.ward_id, w.ward_name, w.zone
ORDER BY total_collected DESC;

-- 8. Annual revenue summary
SELECT
    t.financial_year,
    COUNT(DISTINCT t.property_id)      AS properties_assessed,
    SUM(t.tax_amount)                  AS gross_tax,
    SUM(t.penalty_amount)              AS penalties,
    SUM(t.rebate_amount)               AS rebates,
    COALESCE(SUM(pay.amount_paid), 0)  AS collected
FROM tax_record t
LEFT JOIN payment pay ON t.tax_id = pay.tax_id
GROUP BY t.financial_year
ORDER BY t.financial_year DESC;

-- 9. Payment mode distribution
SELECT
    payment_mode,
    COUNT(*)       AS total_transactions,
    SUM(amount_paid) AS total_amount,
    ROUND(AVG(amount_paid), 2) AS avg_amount
FROM payment
GROUP BY payment_mode
ORDER BY total_amount DESC;

-- 10. Property type wise tax demand
SELECT
    p.property_type,
    COUNT(p.property_id) AS count,
    SUM(p.annual_value)  AS total_annual_value,
    SUM(t.tax_amount)    AS total_tax_demand
FROM property    p
LEFT JOIN tax_record t ON p.property_id = t.property_id
GROUP BY p.property_type
ORDER BY total_tax_demand DESC;

-- ═══════════════════════════════════════════════════════════
--  SECTION F: Subqueries
-- ═══════════════════════════════════════════════════════════

-- 11. Properties with tax > average tax amount
SELECT
    p.property_number,
    p.property_type,
    t.tax_amount
FROM property    p
JOIN tax_record  t ON p.property_id = t.property_id
WHERE t.tax_amount > (
    SELECT AVG(tax_amount) FROM tax_record
)
ORDER BY t.tax_amount DESC;

-- 12. Owners who have never paid tax (no payment record)
SELECT
    CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
    o.email,
    o.phone
FROM owner o
WHERE o.owner_id IN (
    SELECT p.owner_id
    FROM   property p
    JOIN   tax_record t ON p.property_id = t.property_id
    WHERE  t.tax_id NOT IN (
        SELECT DISTINCT tax_id FROM payment
    )
);

-- 13. Ward with highest outstanding dues
SELECT
    w.ward_name,
    SUM(t.total_due) - COALESCE(SUM(pay.amount_paid), 0) AS outstanding
FROM ward        w
JOIN property    p   ON w.ward_id     = p.ward_id
JOIN tax_record  t   ON p.property_id = t.property_id
LEFT JOIN payment pay ON t.tax_id     = pay.tax_id
GROUP BY w.ward_id, w.ward_name
HAVING outstanding = (
    SELECT MAX(outstanding_sub) FROM (
        SELECT SUM(ts.total_due) - COALESCE(SUM(ps.amount_paid), 0) AS outstanding_sub
        FROM   ward        ws
        JOIN   property    pps  ON ws.ward_id      = pps.ward_id
        JOIN   tax_record  ts   ON pps.property_id = ts.property_id
        LEFT JOIN payment  ps   ON ts.tax_id       = ps.tax_id
        GROUP BY ws.ward_id
    ) sub
);

-- 14. Properties in top-demand ward
SELECT
    p.property_number,
    p.property_type,
    CONCAT(o.first_name, ' ', o.last_name) AS owner
FROM property p
JOIN owner o ON p.owner_id = o.owner_id
WHERE p.ward_id = (
    SELECT ward_id
    FROM (
        SELECT w2.ward_id, SUM(t2.total_due) AS total
        FROM   ward w2
        JOIN   property   p2 ON w2.ward_id     = p2.ward_id
        JOIN   tax_record t2 ON p2.property_id = t2.property_id
        GROUP BY w2.ward_id
        ORDER BY total DESC
        LIMIT 1
    ) top_ward
);

-- 15. HAVING – Wards with more than 1 overdue property
SELECT
    w.ward_name,
    COUNT(*) AS overdue_count
FROM ward        w
JOIN property    p ON w.ward_id     = p.ward_id
JOIN tax_record  t ON p.property_id = t.property_id
WHERE t.status = 'Overdue'
GROUP BY w.ward_id, w.ward_name
HAVING overdue_count > 0
ORDER BY overdue_count DESC;
