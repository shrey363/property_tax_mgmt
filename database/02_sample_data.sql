-- ============================================================
--  Property Tax Management System
--  File: 02_sample_data.sql
--  Description: DML – Sample Data (5-10 rows per table)
-- ============================================================

USE property_tax_db;

-- ─────────────────────────────────────────
-- Users
-- ─────────────────────────────────────────
INSERT INTO users (username, password_hash, role, full_name, email) VALUES
('admin',   SHA2('admin123', 256),  'admin',  'System Administrator', 'admin@ptms.gov.in'),
('clerk1',  SHA2('Clerk@123', 256),  'clerk',  'Ramesh Kumar',         'ramesh.kumar@ptms.gov.in'),
('clerk2',  SHA2('Clerk@456', 256),  'clerk',  'Sunita Sharma',        'sunita.sharma@ptms.gov.in'),
('viewer1', SHA2('View@123',  256),  'viewer', 'Anjali Rao',           'anjali.rao@ptms.gov.in'),
('viewer2', SHA2('View@456',  256),  'viewer', 'Pradeep Nair',         'pradeep.nair@ptms.gov.in');

-- ─────────────────────────────────────────
-- Wards
-- ─────────────────────────────────────────
INSERT INTO ward (ward_name, ward_number, zone, officer_name, contact_email) VALUES
('Koramangala Ward',   'W-001', 'South Zone', 'Arun Mehta',     'w001@ptms.gov.in'),
('Indiranagar Ward',   'W-002', 'East Zone',  'Priya Desai',    'w002@ptms.gov.in'),
('Jayanagar Ward',     'W-003', 'South Zone', 'Suresh Patil',   'w003@ptms.gov.in'),
('Whitefield Ward',    'W-004', 'East Zone',  'Kavitha Reddy',  'w004@ptms.gov.in'),
('Rajajinagar Ward',   'W-005', 'West Zone',  'Mohan Pillai',   'w005@ptms.gov.in'),
('Malleswaram Ward',   'W-006', 'North Zone', 'Deepa Iyer',     'w006@ptms.gov.in'),
('Hebbal Ward',        'W-007', 'North Zone', 'Ravi Shankar',   'w007@ptms.gov.in');

-- ─────────────────────────────────────────
-- Owners
-- ─────────────────────────────────────────
INSERT INTO owner (first_name, last_name, email, phone, address, aadhar_number, pan_number) VALUES
('Vikram',   'Singh',    'vikram.singh@email.com',   '9876543210', '12, MG Road, Bengaluru - 560001',          '123456789012', 'ABCDE1234F'),
('Meena',    'Iyer',     'meena.iyer@email.com',     '9876543211', '45, Brigade Road, Bengaluru - 560025',     '234567890123', 'BCDEF2345G'),
('Suresh',   'Patil',    'suresh.patil@email.com',   '9876543212', '78, Residency Road, Bengaluru - 560025',   '345678901234', 'CDEFG3456H'),
('Anita',    'Kulkarni', 'anita.kulkarni@email.com', '9876543213', '23, Commercial St, Bengaluru - 560001',    '456789012345', 'DEFGH4567I'),
('Rajesh',   'Nair',     'rajesh.nair@email.com',    '9876543214', '56, Church St, Bengaluru - 560001',        '567890123456', 'EFGHI5678J'),
('Pooja',    'Reddy',    'pooja.reddy@email.com',    '9876543215', '89, Koramangala 5th Block, BLR - 560095',  '678901234567', 'FGHIJ6789K'),
('Arun',     'Sharma',   'arun.sharma@email.com',    '9876543216', '34, Indiranagar 1st Stage, BLR - 560038', '789012345678', 'GHIJK7890L'),
('Lakshmi',  'Bhat',     'lakshmi.bhat@email.com',   '9876543217', '67, Jayanagar 4th Block, BLR - 560041',   '890123456789', 'HIJKL8901M'),
('Praveen',  'Kumar',    'praveen.kumar@email.com',  '9876543218', '12, Whitefield Main Road, BLR - 560066',  '901234567890', 'IJKLM9012N'),
('Deepa',    'Menon',    'deepa.menon@email.com',    '9876543219', '45, Rajajinagar 2nd Block, BLR - 560010', '012345678901', 'JKLMN0123O');

-- ─────────────────────────────────────────
-- Properties
-- ─────────────────────────────────────────
INSERT INTO property (property_number, owner_id, ward_id, address, property_type, area_sqft, floors, construction_year, annual_value) VALUES
('PROP-KRM-001', 1,  1, '12, MG Road, Koramangala, BLR',          'Commercial',    2500.00, 3, 2005, 1800000.00),
('PROP-IND-001', 2,  2, '45, 100 Feet Road, Indiranagar, BLR',    'Residential',   1800.00, 2, 2010, 1200000.00),
('PROP-JYN-001', 3,  3, '78, 11th Main, Jayanagar, BLR',          'Residential',   1200.00, 1, 1998, 850000.00),
('PROP-WFD-001', 4,  4, '23, ITPL Road, Whitefield, BLR',         'Commercial',    3500.00, 4, 2015, 2500000.00),
('PROP-RJN-001', 5,  5, '56, Dr Raj Kumar Road, Rajajinagar, BLR','Residential',   2000.00, 2, 2008, 1400000.00),
('PROP-KRM-002', 6,  1, '89, 5th Block, Koramangala, BLR',        'Residential',   1500.00, 2, 2012, 1100000.00),
('PROP-IND-002', 7,  2, '34, 12th Main, Indiranagar, BLR',        'Residential',   1700.00, 2, 2011, 1250000.00),
('PROP-JYN-002', 8,  3, '67, 4th Block, Jayanagar, BLR',          'Residential',   900.00,  1, 1990, 700000.00),
('PROP-WFD-002', 9,  4, '12, EPIP Zone, Whitefield, BLR',         'Industrial',    5000.00, 1, 2016, 3500000.00),
('PROP-MLW-001', 10, 6, '45, 8th Cross, Malleswaram, BLR',        'Residential',   1100.00, 2, 2003, 900000.00);

-- ─────────────────────────────────────────
-- Tax Records
-- ─────────────────────────────────────────
INSERT INTO tax_record (property_id, financial_year, tax_amount, penalty_amount, rebate_amount, total_due, due_date, status) VALUES
(1,  '2023-2024', 36000.00,  3600.00, 0.00,     39600.00, '2023-07-31', 'Paid'),
(2,  '2023-2024', 24000.00,  0.00,    1200.00,  22800.00, '2023-07-31', 'Paid'),
(3,  '2023-2024', 17000.00,  0.00,    0.00,     17000.00, '2023-07-31', 'Paid'),
(4,  '2023-2024', 50000.00,  5000.00, 0.00,     55000.00, '2023-07-31', 'Overdue'),
(5,  '2023-2024', 28000.00,  0.00,    1400.00,  26600.00, '2023-07-31', 'Paid'),
(6,  '2024-2025', 22000.00,  0.00,    0.00,     22000.00, '2024-07-31', 'Pending'),
(7,  '2024-2025', 25000.00,  0.00,    1250.00,  23750.00, '2024-07-31', 'Paid'),
(8,  '2024-2025', 14000.00,  1400.00, 0.00,     15400.00, '2024-07-31', 'Overdue'),
(9,  '2024-2025', 70000.00,  0.00,    0.00,     70000.00, '2024-07-31', 'Partial'),
(10, '2024-2025', 18000.00,  0.00,    900.00,   17100.00, '2024-07-31', 'Pending');

-- ─────────────────────────────────────────
-- Payments
-- ─────────────────────────────────────────
INSERT INTO payment (tax_id, amount_paid, payment_mode, transaction_ref, receipt_number, remarks) VALUES
(1, 39600.00, 'Online', 'TXN20230801001', 'RCP-2023-0001', 'Full payment'),
(2, 22800.00, 'UPI',    'TXN20230815002', 'RCP-2023-0002', 'Full payment with rebate'),
(3, 17000.00, 'Cash',   NULL,             'RCP-2023-0003', 'Full cash payment'),
(5, 26600.00, 'NEFT',   'TXN20230720005', 'RCP-2023-0005', 'Full payment with early rebate'),
(7, 23750.00, 'Online', 'TXN20240810007', 'RCP-2024-0007', 'Full payment'),
(9, 35000.00, 'Cheque', 'CHQ20240825009', 'RCP-2024-0009', 'Partial – first instalment');
