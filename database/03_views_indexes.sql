-- ============================================================
--  Property Tax Management System
--  File: 03_views_indexes.sql
--  Description: Views & Indexes
-- ============================================================

USE property_tax_db;

-- ─────────────────────────────────────────
-- VIEW 1: v_property_tax_summary
--   Full summary joining property, owner, ward, tax_record
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW v_property_tax_summary AS
SELECT
    p.property_id,
    p.property_number,
    p.address            AS property_address,
    p.property_type,
    p.area_sqft,
    p.annual_value,
    CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
    o.email              AS owner_email,
    o.phone              AS owner_phone,
    w.ward_number,
    w.ward_name,
    w.zone,
    t.tax_id,
    t.financial_year,
    t.tax_amount,
    t.penalty_amount,
    t.rebate_amount,
    t.total_due,
    t.due_date,
    t.status             AS tax_status
FROM property     p
JOIN owner        o ON p.owner_id    = o.owner_id
JOIN ward         w ON p.ward_id     = w.ward_id
LEFT JOIN tax_record t ON p.property_id = t.property_id;

-- ─────────────────────────────────────────
-- VIEW 2: v_defaulters
--   Properties with Overdue or Pending tax
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW v_defaulters AS
SELECT
    p.property_number,
    CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
    o.phone,
    o.email,
    w.ward_name,
    w.ward_number,
    t.financial_year,
    t.total_due,
    t.penalty_amount,
    t.due_date,
    t.status,
    DATEDIFF(CURDATE(), t.due_date) AS days_overdue
FROM tax_record t
JOIN property p ON t.property_id = p.property_id
JOIN owner    o ON p.owner_id    = o.owner_id
JOIN ward     w ON p.ward_id     = w.ward_id
WHERE t.status IN ('Overdue', 'Pending')
ORDER BY days_overdue DESC;

-- ─────────────────────────────────────────
-- VIEW 3: v_ward_collection_summary
--   Ward-wise total collected vs total due
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW v_ward_collection_summary AS
SELECT
    w.ward_id,
    w.ward_number,
    w.ward_name,
    w.zone,
    w.officer_name,
    COUNT(DISTINCT p.property_id)               AS total_properties,
    COUNT(DISTINCT t.tax_id)                    AS total_tax_records,
    SUM(t.total_due)                            AS total_demand,
    COALESCE(SUM(pay.amount_paid), 0)           AS total_collected,
    SUM(t.total_due) - COALESCE(SUM(pay.amount_paid), 0) AS outstanding
FROM ward w
LEFT JOIN property   p   ON w.ward_id    = p.ward_id
LEFT JOIN tax_record t   ON p.property_id = t.property_id
LEFT JOIN payment    pay ON t.tax_id      = pay.tax_id
GROUP BY w.ward_id, w.ward_number, w.ward_name, w.zone, w.officer_name;

-- ─────────────────────────────────────────
-- VIEW 4: v_payment_history
--   Full payment history with property + owner
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW v_payment_history AS
SELECT
    pay.receipt_number,
    pay.payment_date,
    pay.amount_paid,
    pay.payment_mode,
    pay.transaction_ref,
    t.financial_year,
    t.total_due,
    p.property_number,
    p.property_type,
    CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
    w.ward_name
FROM payment     pay
JOIN tax_record  t   ON pay.tax_id       = t.tax_id
JOIN property    p   ON t.property_id    = p.property_id
JOIN owner       o   ON p.owner_id       = o.owner_id
JOIN ward        w   ON p.ward_id        = w.ward_id
ORDER BY pay.payment_date DESC;

-- ─────────────────────────────────────────
-- VIEW 5: v_annual_revenue
--   Year-wise revenue totals
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW v_annual_revenue AS
SELECT
    t.financial_year,
    COUNT(DISTINCT t.property_id)      AS properties_assessed,
    SUM(t.tax_amount)                  AS gross_tax_demand,
    SUM(t.penalty_amount)              AS total_penalties,
    SUM(t.rebate_amount)               AS total_rebates,
    SUM(t.total_due)                   AS net_demand,
    COALESCE(SUM(pay.amount_paid), 0)  AS total_collected,
    SUM(t.total_due) - COALESCE(SUM(pay.amount_paid), 0) AS uncollected
FROM tax_record t
LEFT JOIN payment pay ON t.tax_id = pay.tax_id
GROUP BY t.financial_year
ORDER BY t.financial_year DESC;

-- ─────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────

-- Speed up property lookups by owner
CREATE INDEX idx_property_owner_id
    ON property(owner_id);

-- Speed up property lookups by ward
CREATE INDEX idx_property_ward_id
    ON property(ward_id);

-- Speed up tax record lookups by status
CREATE INDEX idx_tax_status
    ON tax_record(status);

-- Speed up tax record lookups by financial year
CREATE INDEX idx_tax_financial_year
    ON tax_record(financial_year);

-- Speed up payment lookups by date
CREATE INDEX idx_payment_date
    ON payment(payment_date);

-- Speed up payment lookups by tax
CREATE INDEX idx_payment_tax_id
    ON payment(tax_id);

-- Full-text on owner name fields for search
CREATE INDEX idx_owner_name
    ON owner(last_name, first_name);
