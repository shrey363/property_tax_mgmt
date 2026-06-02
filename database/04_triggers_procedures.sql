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

DELIMITER ;