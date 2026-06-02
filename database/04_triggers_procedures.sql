USE property_tax_db;

DELIMITER $$

-- ─────────────────────────────────────────
-- SP 1: sp_calculate_tax
-- ─────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_calculate_tax $$

CREATE PROCEDURE sp_calculate_tax (
    IN  p_property_id    INT,
    IN  p_financial_year VARCHAR(9),
    IN  p_due_date       DATE,
    OUT p_tax_id         INT,
    OUT p_message        VARCHAR(255)
)
BEGIN

    DECLARE v_annual_value    DECIMAL(15,2);
    DECLARE v_property_type   VARCHAR(30);
    DECLARE v_tax_rate        DECIMAL(5,4);
    DECLARE v_tax_amount      DECIMAL(12,2);
    DECLARE v_existing_tax_id INT DEFAULT NULL;

    -- Fetch property details
    SELECT annual_value, property_type
    INTO v_annual_value, v_property_type
    FROM property
    WHERE property_id = p_property_id
      AND is_active = 1;

    -- Check property exists
    IF v_annual_value IS NULL THEN

        SET p_message = 'ERROR: Property not found or inactive.';
        SET p_tax_id = -1;

    ELSE

        -- Tax rate by property type
        SET v_tax_rate = CASE v_property_type
            WHEN 'Residential'  THEN 0.0200
            WHEN 'Commercial'   THEN 0.0300
            WHEN 'Industrial'   THEN 0.0400
            WHEN 'Agricultural' THEN 0.0050
            ELSE 0.0200
        END;

        -- Calculate tax amount
        SET v_tax_amount = ROUND(v_annual_value * v_tax_rate, 2);

        -- Check existing tax record
        SELECT tax_id
        INTO v_existing_tax_id
        FROM tax_record
        WHERE property_id = p_property_id
          AND financial_year = p_financial_year
        LIMIT 1;

        -- Update existing record
        IF v_existing_tax_id IS NOT NULL THEN

            UPDATE tax_record
            SET tax_amount = v_tax_amount,
                total_due = v_tax_amount + penalty_amount - rebate_amount,
                updated_at = NOW()
            WHERE tax_id = v_existing_tax_id;

            SET p_tax_id = v_existing_tax_id;

            SET p_message = CONCAT(
                'UPDATED: Tax record ',
                v_existing_tax_id,
                ' for FY ',
                p_financial_year
            );

        ELSE

            -- Insert new tax record
            INSERT INTO tax_record (
                property_id,
                financial_year,
                tax_amount,
                total_due,
                due_date
            )
            VALUES (
                p_property_id,
                p_financial_year,
                v_tax_amount,
                v_tax_amount,
                p_due_date
            );

            SET p_tax_id = LAST_INSERT_ID();

            SET p_message = CONCAT(
                'CREATED: Tax record ',
                p_tax_id,
                ' for FY ',
                p_financial_year,
                ' | Amount: ',
                v_tax_amount
            );

        END IF;

    END IF;

END $$


-- ─────────────────────────────────────────
-- SP 2: sp_record_payment
-- ─────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_record_payment $$

CREATE PROCEDURE sp_record_payment (
    IN  p_tax_id           INT,
    IN  p_amount           DECIMAL(12,2),
    IN  p_payment_mode     VARCHAR(20),
    IN  p_transaction_ref  VARCHAR(100),
    OUT p_receipt_number   VARCHAR(30),
    OUT p_message          VARCHAR(255)
)
BEGIN
    DECLARE v_exists     INT DEFAULT 0;
    DECLARE v_status     VARCHAR(20);
    DECLARE v_total_due  DECIMAL(12,2);
    DECLARE v_total_paid DECIMAL(12,2);
    DECLARE v_next_id    INT DEFAULT 1;

    -- Validate existence of tax record
    SELECT COUNT(*) INTO v_exists FROM tax_record WHERE tax_id = p_tax_id;

    IF v_exists = 0 THEN
        SET p_receipt_number = '';
        SET p_message = 'ERROR: Tax record not found.';
    
    ELSEIF p_amount <= 0 THEN
        SET p_receipt_number = '';
        SET p_message = 'ERROR: Payment amount must be greater than zero.';

    ELSE
        SELECT status, total_due INTO v_status, v_total_due 
        FROM tax_record 
        WHERE tax_id = p_tax_id;

        IF v_status = 'Paid' THEN
            SET p_receipt_number = '';
            SET p_message = 'ERROR: Tax record is already fully paid.';
        
        ELSEIF p_transaction_ref IS NOT NULL AND p_transaction_ref <> '' AND EXISTS(SELECT 1 FROM payment WHERE transaction_ref = p_transaction_ref) THEN
            SET p_receipt_number = '';
            SET p_message = 'ERROR: Duplicate transaction reference.';
        
        ELSE
            SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid 
            FROM payment 
            WHERE tax_id = p_tax_id;

            IF p_amount > (v_total_due - v_total_paid) THEN
                SET p_receipt_number = '';
                SET p_message = CONCAT('ERROR: Payment amount exceeds outstanding balance of ', (v_total_due - v_total_paid));
            ELSE
                -- Generate unique receipt number
                SELECT COALESCE(MAX(payment_id), 0) + 1 INTO v_next_id FROM payment;
                SET p_receipt_number = CONCAT('RCP-', YEAR(NOW()), '-', LPAD(v_next_id, 4, '0'));

                INSERT INTO payment (
                    tax_id,
                    amount_paid,
                    payment_date,
                    payment_mode,
                    transaction_ref,
                    receipt_number,
                    remarks
                )
                VALUES (
                    p_tax_id,
                    p_amount,
                    NOW(),
                    p_payment_mode,
                    IF(p_transaction_ref = '', NULL, p_transaction_ref),
                    p_receipt_number,
                    'Recorded via sp_record_payment'
                );

                SET p_message = CONCAT('SUCCESS: Payment recorded. Receipt: ', p_receipt_number);
            END IF;
        END IF;
    END IF;
END $$


-- ─────────────────────────────────────────
-- SP 3: sp_apply_penalty
-- ─────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_apply_penalty $$

CREATE PROCEDURE sp_apply_penalty (
    OUT p_records_updated INT,
    OUT p_message         VARCHAR(255)
)
BEGIN
    DECLARE v_count INT DEFAULT 0;

    -- Update status to Overdue and apply 10% penalty for records past due date that are Pending/Partial
    UPDATE tax_record
    SET status = 'Overdue',
        penalty_amount = ROUND(tax_amount * 0.10, 2),
        updated_at = NOW()
    WHERE due_date < CURDATE()
      AND status IN ('Pending', 'Partial')
      AND penalty_amount = 0.00;

    SET v_count = ROW_COUNT();
    SET p_records_updated = v_count;
    SET p_message = CONCAT('SUCCESS: Penalties applied to ', v_count, ' overdue records.');
END $$


-- ─────────────────────────────────────────
-- SP 4: sp_get_defaulters_report
-- ─────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_get_defaulters_report $$

CREATE PROCEDURE sp_get_defaulters_report (
    IN p_ward_id INT
)
BEGIN
    IF p_ward_id IS NULL THEN
        SELECT * FROM v_defaulters;
    ELSE
        SELECT vd.*
        FROM v_defaulters vd
        JOIN property p ON vd.property_number = p.property_number
        WHERE p.ward_id = p_ward_id;
    END IF;
END $$


-- ─────────────────────────────────────────
-- SP 5: sp_ward_collection_report
-- ─────────────────────────────────────────
DROP PROCEDURE IF EXISTS sp_ward_collection_report $$

CREATE PROCEDURE sp_ward_collection_report (
    IN p_financial_year VARCHAR(9)
)
BEGIN
    SELECT
        w.ward_id,
        w.ward_number,
        w.ward_name,
        w.zone,
        w.officer_name,
        COUNT(DISTINCT p.property_id)               AS total_properties,
        COUNT(DISTINCT t.tax_id)                    AS total_tax_records,
        COALESCE(SUM(t.total_due), 0)               AS total_demand,
        COALESCE(SUM(pay.amount_paid), 0)           AS total_collected,
        COALESCE(SUM(t.total_due), 0) - COALESCE(SUM(pay.amount_paid), 0) AS outstanding
    FROM ward w
    LEFT JOIN property   p   ON w.ward_id    = p.ward_id
    LEFT JOIN tax_record t   ON p.property_id = t.property_id AND (p_financial_year IS NULL OR t.financial_year = p_financial_year)
    LEFT JOIN payment    pay ON t.tax_id      = pay.tax_id
    GROUP BY w.ward_id, w.ward_number, w.ward_name, w.zone, w.officer_name;
END $$


-- ─────────────────────────────────────────
-- TRIGGER 1: trg_before_tax_record_insert
-- ─────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_before_tax_record_insert $$

CREATE TRIGGER trg_before_tax_record_insert
BEFORE INSERT ON tax_record
FOR EACH ROW
BEGIN
    SET NEW.total_due = NEW.tax_amount + NEW.penalty_amount - NEW.rebate_amount;
END $$


-- ─────────────────────────────────────────
-- TRIGGER 2: trg_before_tax_record_update
-- ─────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_before_tax_record_update $$

CREATE TRIGGER trg_before_tax_record_update
BEFORE UPDATE ON tax_record
FOR EACH ROW
BEGIN
    SET NEW.total_due = NEW.tax_amount + NEW.penalty_amount - NEW.rebate_amount;
END $$


-- ─────────────────────────────────────────
-- TRIGGER 3: trg_after_payment_update_status
-- ─────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_payment_update_status $$

CREATE TRIGGER trg_after_payment_update_status
AFTER INSERT ON payment
FOR EACH ROW
BEGIN
    DECLARE v_total_due  DECIMAL(12,2);
    DECLARE v_total_paid DECIMAL(12,2);
    DECLARE v_status     VARCHAR(20);

    SELECT total_due INTO v_total_due
    FROM tax_record
    WHERE tax_id = NEW.tax_id;

    SELECT COALESCE(SUM(amount_paid), 0) INTO v_total_paid
    FROM payment
    WHERE tax_id = NEW.tax_id;

    IF v_total_paid >= v_total_due THEN
        SET v_status = 'Paid';
    ELSEIF v_total_paid > 0 THEN
        SET v_status = 'Partial';
    ELSE
        SET v_status = 'Pending';
    END IF;

    UPDATE tax_record
    SET status = v_status,
        updated_at = NOW()
    WHERE tax_id = NEW.tax_id;
END $$


-- ─────────────────────────────────────────
-- TRIGGER 4: trg_after_property_annual_value_change
-- ─────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_after_property_annual_value_change $$

CREATE TRIGGER trg_after_property_annual_value_change
AFTER UPDATE ON property
FOR EACH ROW
BEGIN
    DECLARE v_tax_rate DECIMAL(5,4);

    IF OLD.annual_value <> NEW.annual_value OR OLD.property_type <> NEW.property_type THEN
        SET v_tax_rate = CASE NEW.property_type
            WHEN 'Residential'  THEN 0.0200
            WHEN 'Commercial'   THEN 0.0300
            WHEN 'Industrial'   THEN 0.0400
            WHEN 'Agricultural' THEN 0.0050
            ELSE 0.0200
        END;

        UPDATE tax_record
        SET tax_amount = ROUND(NEW.annual_value * v_tax_rate, 2),
            updated_at = NOW()
        WHERE property_id = NEW.property_id
          AND status IN ('Pending', 'Partial', 'Overdue');
    END IF;
END $$


-- ─────────────────────────────────────────
-- TRIGGER 5: trg_before_payment_delete
-- ─────────────────────────────────────────
DROP TRIGGER IF EXISTS trg_before_payment_delete $$

CREATE TRIGGER trg_before_payment_delete
BEFORE DELETE ON payment
FOR EACH ROW
BEGIN
    DECLARE v_status VARCHAR(20);

    SELECT status INTO v_status
    FROM tax_record
    WHERE tax_id = OLD.tax_id;

    IF v_status = 'Paid' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ERROR: Cannot delete payment for a fully paid tax record.';
    END IF;
END $$

DELIMITER ;