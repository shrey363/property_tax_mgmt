-- ============================================================
--  Property Tax Management System
--  File: 01_schema.sql
--  Description: DDL – Database & Table Creation
-- ============================================================

CREATE DATABASE IF NOT EXISTS property_tax_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE property_tax_db;

-- ─────────────────────────────────────────
-- TABLE 1: ward
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ward (
    ward_id       INT            NOT NULL AUTO_INCREMENT,
    ward_name     VARCHAR(100)   NOT NULL,
    ward_number   VARCHAR(20)    NOT NULL UNIQUE,
    zone          VARCHAR(50)    NOT NULL,
    officer_name  VARCHAR(100)   NOT NULL,
    contact_email VARCHAR(150)   NOT NULL,
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_ward PRIMARY KEY (ward_id)
);

-- ─────────────────────────────────────────
-- TABLE 2: owner
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS owner (
    owner_id       INT           NOT NULL AUTO_INCREMENT,
    first_name     VARCHAR(80)   NOT NULL,
    last_name      VARCHAR(80)   NOT NULL,
    email          VARCHAR(150)  NOT NULL UNIQUE,
    phone          VARCHAR(15)   NOT NULL,
    address        VARCHAR(255)  NOT NULL,
    aadhar_number  CHAR(12)      NOT NULL UNIQUE,
    pan_number     VARCHAR(10)   UNIQUE,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_owner PRIMARY KEY (owner_id),
    CONSTRAINT chk_aadhar  CHECK (CHAR_LENGTH(aadhar_number) = 12),
    CONSTRAINT chk_phone   CHECK (CHAR_LENGTH(phone) >= 10)
);

-- ─────────────────────────────────────────
-- TABLE 3: property
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS property (
    property_id       INT              NOT NULL AUTO_INCREMENT,
    property_number   VARCHAR(30)      NOT NULL UNIQUE,
    owner_id          INT              NOT NULL,
    ward_id           INT              NOT NULL,
    address           VARCHAR(255)     NOT NULL,
    property_type     ENUM('Residential','Commercial','Industrial','Agricultural')
                                       NOT NULL DEFAULT 'Residential',
    area_sqft         DECIMAL(10,2)    NOT NULL,
    floors            TINYINT UNSIGNED NOT NULL DEFAULT 1,
    construction_year YEAR             NOT NULL,
    annual_value      DECIMAL(15,2)    NOT NULL,   -- Annual Rental/Property Value
    is_active         TINYINT(1)       NOT NULL DEFAULT 1,
    registered_at     DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_property    PRIMARY KEY (property_id),
    CONSTRAINT fk_prop_owner  FOREIGN KEY (owner_id) REFERENCES owner(owner_id)
                               ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_prop_ward   FOREIGN KEY (ward_id)  REFERENCES ward(ward_id)
                               ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_area       CHECK (area_sqft > 0),
    CONSTRAINT chk_annual_val CHECK (annual_value >= 0)
);

-- ─────────────────────────────────────────
-- TABLE 4: tax_record
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tax_record (
    tax_id          INT              NOT NULL AUTO_INCREMENT,
    property_id     INT              NOT NULL,
    financial_year  VARCHAR(9)       NOT NULL,   -- e.g. '2024-2025'
    tax_amount      DECIMAL(12,2)    NOT NULL,
    penalty_amount  DECIMAL(12,2)    NOT NULL DEFAULT 0.00,
    rebate_amount   DECIMAL(12,2)    NOT NULL DEFAULT 0.00,
    total_due       DECIMAL(12,2)    NOT NULL,
    due_date        DATE             NOT NULL,
    status          ENUM('Pending','Partial','Paid','Overdue','Waived')
                                     NOT NULL DEFAULT 'Pending',
    generated_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_tax_record      PRIMARY KEY (tax_id),
    CONSTRAINT fk_tax_property    FOREIGN KEY (property_id) REFERENCES property(property_id)
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_prop_year       UNIQUE (property_id, financial_year),
    CONSTRAINT chk_tax_amount     CHECK (tax_amount >= 0),
    CONSTRAINT chk_penalty        CHECK (penalty_amount >= 0),
    CONSTRAINT chk_rebate         CHECK (rebate_amount >= 0)
);

-- ─────────────────────────────────────────
-- TABLE 5: payment
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payment (
    payment_id      INT              NOT NULL AUTO_INCREMENT,
    tax_id          INT              NOT NULL,
    amount_paid     DECIMAL(12,2)    NOT NULL,
    payment_date    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_mode    ENUM('Cash','Cheque','Online','DD','NEFT','UPI')
                                     NOT NULL DEFAULT 'Online',
    transaction_ref VARCHAR(100)     UNIQUE,
    receipt_number  VARCHAR(30)      NOT NULL UNIQUE,
    remarks         VARCHAR(255)     DEFAULT NULL,
    CONSTRAINT pk_payment     PRIMARY KEY (payment_id),
    CONSTRAINT fk_pay_tax     FOREIGN KEY (tax_id) REFERENCES tax_record(tax_id)
                               ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_amount_paid CHECK (amount_paid > 0)
);

-- ─────────────────────────────────────────
-- TABLE 6: users  (application login)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id       INT           NOT NULL AUTO_INCREMENT,
    username      VARCHAR(60)   NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role          ENUM('admin','clerk','viewer') NOT NULL DEFAULT 'viewer',
    full_name     VARCHAR(150)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    is_active     TINYINT(1)    NOT NULL DEFAULT 1,
    last_login    DATETIME      DEFAULT NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_users PRIMARY KEY (user_id)
);
