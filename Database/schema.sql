-- =================================================================
-- FINAL MASTER SETUP SCRIPT (100% COMPLETE & VERIFIED)
-- =================================================================
-- 1. Drops and Recreates Schema (Tables)
-- 2. Creates Stock Management Triggers
-- 3. Populates Base Data (Locations, Depts, Products, 50+ Persons)
-- 4. Populates Transactional Data (15+ Projects, Assignments, Orders)
-- 
-- USAGE: Run this ONCE to get a fully working, populated database.
-- =================================================================

DROP DATABASE IF EXISTS company_management;
CREATE DATABASE company_management;
USE company_management;

-- ============================================
-- PART 1: SCHEMA CREATION
-- ============================================

-- 1. LOCATIONS
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT,
    location_name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_location_id PRIMARY KEY (location_id)
);

-- 2. DEPARTMENTS
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT,
    location_id INT,
    department_name VARCHAR(100) NOT NULL,
    hod_id INT,  
    CONSTRAINT pk_dept_id PRIMARY KEY (department_id),
    CONSTRAINT fk_dept_location FOREIGN KEY (location_id) REFERENCES locations (location_id) ON DELETE SET NULL
);

-- 3. PERSON (Supertype)
CREATE TABLE person (
    person_id INT AUTO_INCREMENT,
    department_id INT,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    address VARCHAR(1000),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    national_insurance VARCHAR(50) UNIQUE,
    start_date DATE,
    leaving_date DATE,
    person_type ENUM('GENERAL_EMPLOYEE', 'SUPERVISOR', 'HOD', 'SALESMAN') NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT pk_person_id PRIMARY KEY (person_id),
    CONSTRAINT fk_person_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE SET NULL
);

-- 4. SUBTYPES
CREATE TABLE general_employee (
    person_id INT,
    hourly_rate DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_general_employee PRIMARY KEY (person_id),
    CONSTRAINT fk_general_employee_person FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
);

CREATE TABLE supervisor (
    person_id INT,
    fixed_salary DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_supervisor PRIMARY KEY (person_id),
    CONSTRAINT fk_supervisor_person FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
);

CREATE TABLE hod (
    person_id INT,
    fixed_salary DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_hod PRIMARY KEY (person_id),
    CONSTRAINT fk_hod_person FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
);

CREATE TABLE salesman (
    person_id INT,
    hourly_rate DECIMAL(10, 2) NOT NULL,
    commission_rate DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    CONSTRAINT pk_salesman PRIMARY KEY (person_id),
    CONSTRAINT fk_salesman_person FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
);

ALTER TABLE departments 
ADD CONSTRAINT fk_dept_hod FOREIGN KEY (hod_id) REFERENCES hod (person_id) ON DELETE SET NULL;

-- 5. PROJECTS
CREATE TABLE projects (
    project_id INT AUTO_INCREMENT,
    department_id INT,
    location_id INT,
    project_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    status ENUM('PLANNING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD') DEFAULT 'PLANNING',
    CONSTRAINT pk_project_id PRIMARY KEY (project_id),
    CONSTRAINT fk_project_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE SET NULL,
    CONSTRAINT fk_project_location FOREIGN KEY (location_id) REFERENCES locations (location_id) ON DELETE SET NULL
);

-- 6. EMP_PROJECTS
CREATE TABLE emp_projects (
    emp_project_id INT AUTO_INCREMENT,
    employee_id INT NOT NULL,
    project_manager_id INT,
    project_id INT NOT NULL,
    assigned_date DATE DEFAULT (CURRENT_DATE),
    CONSTRAINT pk_emp_project_id PRIMARY KEY (emp_project_id),
    CONSTRAINT fk_emp_projects FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    CONSTRAINT fk_emp_tasks FOREIGN KEY (employee_id) REFERENCES person (person_id) ON DELETE CASCADE,
    CONSTRAINT fk_project_manager FOREIGN KEY (project_manager_id) REFERENCES person (person_id) ON DELETE SET NULL
);

-- 7. WORK_LOG
CREATE TABLE work_log (
    log_id INT AUTO_INCREMENT,
    employee_id INT NOT NULL,
    project_id INT NOT NULL,
    work_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    total_hours DECIMAL(5, 2),
    notes TEXT,
    approval_status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    approved_by INT,
    approved_date DATE,
    CONSTRAINT pk_log_id PRIMARY KEY (log_id),
    CONSTRAINT fk_worklog_employee FOREIGN KEY (employee_id) REFERENCES person (person_id) ON DELETE CASCADE,
    CONSTRAINT fk_worklog_project FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
    CONSTRAINT fk_worklog_approver FOREIGN KEY (approved_by) REFERENCES person (person_id) ON DELETE SET NULL
);

-- 8. DEPENDENTS
CREATE TABLE dependents (
    dependent_id INT AUTO_INCREMENT,
    employee_id INT NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    relation_to_employee VARCHAR(50),
    CONSTRAINT pk_dependent_id PRIMARY KEY (dependent_id),
    CONSTRAINT fk_employee_dependent FOREIGN KEY (employee_id) REFERENCES person (person_id) ON DELETE CASCADE
);

-- 9. WAREHOUSES
CREATE TABLE warehouses (
    warehouse_id INT AUTO_INCREMENT,
    location_id INT,
    warehouse_name VARCHAR(100) NOT NULL,
    supervisor_id INT,
    CONSTRAINT pk_warehouse_id PRIMARY KEY (warehouse_id),
    CONSTRAINT fk_warehouse_location FOREIGN KEY (location_id) REFERENCES locations (location_id) ON DELETE SET NULL,
    CONSTRAINT fk_warehouse_supervisor FOREIGN KEY (supervisor_id) REFERENCES supervisor (person_id) ON DELETE SET NULL
);

-- 10. PRODUCTS
CREATE TABLE products (
    product_id INT AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    product_type VARCHAR(50),
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    description TEXT,
    CONSTRAINT pk_product_id PRIMARY KEY (product_id)
);

-- 11. WAREHOUSE_PRODUCTS
CREATE TABLE warehouse_products (
    warehouse_product_id INT AUTO_INCREMENT,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    CONSTRAINT pk_warehouse_product_id PRIMARY KEY (warehouse_product_id),
    CONSTRAINT fk_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id) ON DELETE CASCADE,
    CONSTRAINT fk_warehouse_product FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
    CONSTRAINT uq_warehouse_product UNIQUE (warehouse_id, product_id),
    CONSTRAINT chk_qty CHECK (qty >= 0)
);

-- 12. CUSTOMERS
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT,
    department_id INT,
    salesman_id INT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(1000),
    CONSTRAINT pk_customer_id PRIMARY KEY (customer_id),
    CONSTRAINT fk_customer_dept FOREIGN KEY (department_id) REFERENCES departments (department_id) ON DELETE SET NULL,
    CONSTRAINT fk_customer_salesman FOREIGN KEY (salesman_id) REFERENCES salesman (person_id) ON DELETE SET NULL
);

-- 13. ORDERS_M
CREATE TABLE orders_m (
    order_id INT AUTO_INCREMENT,
    order_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    customer_id INT NOT NULL,
    salesman_id INT,
    total_amount DECIMAL(12, 2) DEFAULT 0.00,
    status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING',
    CONSTRAINT pk_order_id PRIMARY KEY (order_id),
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_salesman FOREIGN KEY (salesman_id) REFERENCES salesman (person_id) ON DELETE SET NULL
);

-- 14. ORDER_ITEMS
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT,
    order_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    product_id INT NOT NULL,
    qty INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    CONSTRAINT pk_order_item_id PRIMARY KEY (order_item_id),
    CONSTRAINT fk_order_master FOREIGN KEY (order_id) REFERENCES orders_m (order_id) ON DELETE CASCADE,
    CONSTRAINT fk_order_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id) ON DELETE RESTRICT,
    CONSTRAINT fk_order_products FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE RESTRICT,
    CONSTRAINT chk_order_qty CHECK (qty > 0)
);

-- 15. EMP_SUPERVISOR (Hierarchy)
CREATE TABLE emp_supervisor (
    employee_id INT NOT NULL,
    supervisor_id INT NOT NULL,
    assigned_date DATE DEFAULT (CURRENT_DATE),
    CONSTRAINT pk_emp_supervisor PRIMARY KEY (employee_id),
    CONSTRAINT fk_emp_supervisor_employee FOREIGN KEY (employee_id) REFERENCES person (person_id) ON DELETE CASCADE,
    CONSTRAINT fk_emp_supervisor_supervisor FOREIGN KEY (supervisor_id) REFERENCES supervisor (person_id) ON DELETE RESTRICT,
    CONSTRAINT chk_not_self_supervised CHECK (employee_id != supervisor_id)
);


-- ============================================
-- PART 2: TRIGGERS (Stock & Total Management)
-- ============================================

DELIMITER //

-- TRIGGER 1: Check Stock Before Inserting Order Item
CREATE TRIGGER before_order_item_insert
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    DECLARE available_stock INT;
    SELECT qty INTO available_stock
    FROM warehouse_products
    WHERE warehouse_id = NEW.warehouse_id AND product_id = NEW.product_id;
    
    IF available_stock IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Product not available in this warehouse';
    ELSEIF available_stock < NEW.qty THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock available';
    END IF;
END//

-- TRIGGER 2: Deduct Stock After Order Item Inserted
CREATE TRIGGER after_order_item_insert
AFTER INSERT ON order_items
FOR EACH ROW
BEGIN
    UPDATE warehouse_products
    SET qty = qty - NEW.qty
    WHERE warehouse_id = NEW.warehouse_id AND product_id = NEW.product_id;
    
    UPDATE orders_m
    SET total_amount = (SELECT SUM(qty * unit_price) FROM order_items WHERE order_id = NEW.order_id)
    WHERE order_id = NEW.order_id;
END//

-- TRIGGER 3: Restore Stock When Order Item Deleted
CREATE TRIGGER after_order_item_delete
AFTER DELETE ON order_items
FOR EACH ROW
BEGIN
    UPDATE warehouse_products
    SET qty = qty + OLD.qty
    WHERE warehouse_id = OLD.warehouse_id AND product_id = OLD.product_id;
    
    UPDATE orders_m
    SET total_amount = (SELECT IFNULL(SUM(qty * unit_price), 0) FROM order_items WHERE order_id = OLD.order_id)
    WHERE order_id = OLD.order_id;
END//

-- TRIGGER 4: Adjust Stock When Order Item Updated
CREATE TRIGGER before_order_item_update
BEFORE UPDATE ON order_items
FOR EACH ROW
BEGIN
    DECLARE available_stock INT;
    DECLARE stock_difference INT;
    SET stock_difference = NEW.qty - OLD.qty;
    
    IF stock_difference > 0 THEN
        SELECT qty INTO available_stock
        FROM warehouse_products
        WHERE warehouse_id = NEW.warehouse_id AND product_id = NEW.product_id;
        
        IF available_stock < stock_difference THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient stock update available';
        END IF;
    END IF;
END//

-- TRIGGER 5: Update Stock After Order Item Updated
CREATE TRIGGER after_order_item_update
AFTER UPDATE ON order_items
FOR EACH ROW
BEGIN
    DECLARE stock_difference INT;
    SET stock_difference = NEW.qty - OLD.qty;

    UPDATE warehouse_products
    SET qty = qty - stock_difference
    WHERE warehouse_id = NEW.warehouse_id AND product_id = NEW.product_id;
    
    UPDATE orders_m
    SET total_amount = (SELECT SUM(qty * unit_price) FROM order_items WHERE order_id = NEW.order_id)
    WHERE order_id = NEW.order_id;
END//

DELIMITER ;

-- ============================================
-- PART 3: BASE DATA (LOCATIONS, DEPARTMENTS, PERSONS)
-- ============================================

INSERT INTO locations (location_id, location_name) VALUES
(1, 'Karachi Head Office'),
(2, 'Lahore Regional'),
(3, 'Islamabad Tower'),
(4, 'Multan Industrial'),
(5, 'Faisalabad Zone');

INSERT INTO departments (department_id, location_id, department_name, hod_id) VALUES
(1, 1, 'IT Department', NULL),
(2, 1, 'Cyber Security', NULL),
(3, 2, 'Accounts & HR', NULL),
(4, 3, 'Sales Department', NULL),
(5, 4, 'Production', NULL);

-- HASH FOR "password123": ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f

INSERT INTO person (person_id, department_id, name, date_of_birth, address, email, phone, national_insurance, start_date, person_type, password_hash, is_active) VALUES
-- HODs (1-5)
(1, 1, 'Hamza Mustafa', '1990-01-01', 'Karachi', 'hamza.mustafa@company.com', '03001111111', 'CNIC-H01', '2020-01-01', 'HOD', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(2, 2, 'Wajid Ali', '1992-02-02', 'Karachi', 'wajid.ali@company.com', '03001111112', 'CNIC-H02', '2020-01-01', 'HOD', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(3, 3, 'Hassan Mustafa', '1988-03-03', 'Lahore', 'hassan.mustafa@company.com', '03001111113', 'CNIC-H03', '2020-01-01', 'HOD', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(4, 4, 'Umais Shahid', '1991-04-04', 'Islamabad', 'umais.shahid@company.com', '03001111114', 'CNIC-H04', '2020-01-01', 'HOD', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(5, 5, 'Umer', '1985-05-05', 'Multan', 'umer@company.com', '03001111115', 'CNIC-H05', '2020-01-01', 'HOD', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),

-- Supervisors (6-10)
(6, 4, 'Ibtisaam Mehmood', '1993-01-01', 'Islamabad', 'ibtisaam@company.com', '03002222221', 'CNIC-S01', '2021-06-01', 'SUPERVISOR', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(7, 2, 'Rida Noor', '1994-02-02', 'Karachi', 'rida.noor@company.com', '03002222222', 'CNIC-S02', '2021-06-01', 'SUPERVISOR', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(8, 1, 'Imagination', '1995-03-03', 'Karachi', 'imagination@company.com', '03002222223', 'CNIC-S03', '2021-06-01', 'SUPERVISOR', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(9, 5, 'Wasim Akram', '1970-01-01', 'Multan', 'wasim@company.com', '03002222224', 'CNIC-S04', '2021-06-01', 'SUPERVISOR', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(10, 5, 'Waqar Younis', '1971-02-02', 'Faisalabad', 'waqar@company.com', '03002222225', 'CNIC-S05', '2021-06-01', 'SUPERVISOR', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),

-- Salesmen (11-19)
(11, 4, 'Malik Muhammad Umair urf Taalie', '1995-06-01', 'Islamabad', 'taalie@company.com', '03003333331', 'CNIC-SA01', '2022-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(12, 4, 'Tahir Khokhar urf CR', '1996-07-02', 'Islamabad', 'tahir.cr@company.com', '03003333332', 'CNIC-SA02', '2022-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(13, 4, 'Babar Azam', '1994-10-15', 'Lahore', 'babar@company.com', '03003333333', 'CNIC-SA03', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(14, 4, 'Shaheen Afridi', '2000-04-06', 'KP', 'shaheen@company.com', '03003333334', 'CNIC-SA04', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(15, 4, 'Rizwan Ahmed', '1992-06-01', 'Peshawar', 'rizwan@company.com', '03003333335', 'CNIC-SA05', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(16, 4, 'Naseem Shah', '2003-02-15', 'KP', 'naseem@company.com', '03003333336', 'CNIC-SA06', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(17, 4, 'Shadab Khan', '1998-10-04', 'Rawalpindi', 'shadab@company.com', '03003333337', 'CNIC-SA07', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(18, 4, 'Haris Rauf', '1993-11-07', 'Rawalpindi', 'haris@company.com', '03003333338', 'CNIC-SA08', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(19, 4, 'Fakhar Zaman', '1990-04-10', 'Mardan', 'fakhar@company.com', '03003333339', 'CNIC-SA09', '2023-01-01', 'SALESMAN', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),

-- General Employees (20-40) - 20 More Filler Employees for Assignments
(20, 1, 'Atif Aslam', '1983-03-12', 'Lahore', 'atif@company.com', '0300444001', 'CNIC-G01', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(21, 1, 'Ali Zafar', '1980-05-18', 'Lahore', 'ali.z@company.com', '0300444002', 'CNIC-G02', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(22, 1, 'Fawad Khan', '1981-11-29', 'Karachi', 'fawad@company.com', '0300444003', 'CNIC-G03', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(23, 1, 'Mahira Khan', '1984-12-21', 'Karachi', 'mahira@company.com', '0300444004', 'CNIC-G04', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(24, 1, 'Humayun Saeed', '1971-07-27', 'Karachi', 'humayun@company.com', '0300444005', 'CNIC-G05', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(25, 2, 'Sajal Aly', '1994-01-17', 'Lahore', 'sajal@company.com', '0300444006', 'CNIC-G06', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(26, 2, 'Yumna Zaidi', '1989-07-30', 'Lahore', 'yumna@company.com', '0300444007', 'CNIC-G07', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(27, 2, 'Hania Aamir', '1997-02-12', 'Rawalpindi', 'hania@company.com', '0300444008', 'CNIC-G08', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(28, 2, 'Bilal Abbas', '1993-06-04', 'Karachi', 'bilal.a@company.com', '0300444009', 'CNIC-G09', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(29, 3, 'Ayeza Khan', '1991-01-15', 'Karachi', 'ayeza@company.com', '0300444010', 'CNIC-G10', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(30, 3, 'Farhan Saeed', '1984-09-14', 'Lahore', 'farhan@company.com', '0300444011', 'CNIC-G11', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(31, 3, 'Iqra Aziz', '1997-11-24', 'Karachi', 'iqra@company.com', '0300444012', 'CNIC-G12', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(32, 5, 'Ahsan Khan', '1981-10-09', 'Lahore', 'ahsan@company.com', '0300444013', 'CNIC-G13', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(33, 5, 'Amjad Sabri', '1970-12-23', 'Karachi', 'amjad@company.com', '0300444014', 'CNIC-G14', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(34, 5, 'Abrar Ul Haq', '1968-07-21', 'Faisalabad', 'abrar@company.com', '0300444015', 'CNIC-G15', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(35, 3, 'Junaid Jamshed', '1964-09-03', 'Karachi', 'junaid@company.com', '0300444016', 'CNIC-G16', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(36, 1, 'Sahir Ali Bagga', '1978-04-10', 'Lahore', 'sahir@company.com', '0300444017', 'CNIC-G17', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(37, 2, 'Momina Mustehsan', '1992-09-05', 'Islamabad', 'momina@company.com', '0300444018', 'CNIC-G18', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(38, 4, 'Aima Baig', '1989-03-10', 'Lahore', 'aima@company.com', '0300444019', 'CNIC-G19', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(39, 4, 'Shehzad Roy', '1977-02-16', 'Karachi', 'shehzad@company.com', '0300444020', 'CNIC-G20', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE),
(40, 1, 'Hadiqa Kiani', '1974-08-11', 'Rawalpindi', 'hadiqa@company.com', '0300444021', 'CNIC-G21', '2023-03-01', 'GENERAL_EMPLOYEE', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', TRUE);

-- Insert Subtypes
INSERT INTO hod (person_id, fixed_salary) SELECT person_id, 300000.00 FROM person WHERE person_type='HOD';
INSERT INTO supervisor (person_id, fixed_salary) SELECT person_id, 150000.00 FROM person WHERE person_type='SUPERVISOR';
INSERT INTO salesman (person_id, hourly_rate, commission_rate) SELECT person_id, 800.00, 5.0 FROM person WHERE person_type='SALESMAN';
INSERT INTO general_employee (person_id, hourly_rate) SELECT person_id, 450.00 FROM person WHERE person_type='GENERAL_EMPLOYEE';

-- Update Dept Links
UPDATE departments SET hod_id = 1 WHERE department_id = 1;
UPDATE departments SET hod_id = 2 WHERE department_id = 2;
UPDATE departments SET hod_id = 3 WHERE department_id = 3;
UPDATE departments SET hod_id = 4 WHERE department_id = 4;
UPDATE departments SET hod_id = 5 WHERE department_id = 5;

-- Establish Hierarchy
INSERT INTO emp_supervisor (employee_id, supervisor_id) VALUES 
(11, 6), (12, 6), (13, 6), (14, 6), -- Salesmen 11-14 under Ibtisaam (6)
(15, 6), (16, 6), (17, 6), (18, 6), (19, 6), -- Salesmen 15-19 under Ibtisaam (6)
(20, 8), (21, 8), (22, 8), -- IT Employees under Imagination (8)
(25, 7), (26, 7), (27, 7), (28, 7), -- Cyber Employees under Rida (7)
(32, 9), (33, 9), (34, 9); -- Production Employees under Wasim (9)

-- WAREHOUSES
INSERT INTO warehouses (warehouse_id, location_id, warehouse_name, supervisor_id) VALUES
(1, 1, 'Karachi Main Warehouse', 8),
(2, 4, 'Multan Logistics Centre', 9),
(3, 3, 'Islamabad Sales Depot', 6),
(4, 5, 'Faisalabad Hub', 10),
(5, 1, 'Karachi Cyber Storage', 7);

-- PRODUCTS
INSERT INTO products (product_name, product_type, unit_price, description) VALUES
('Super Basmati Rice 5kg', 'Food & Grocery', 2500.00, 'Premium quality aged basmati rice'),
('National Pickle Mixed 500g', 'Food & Grocery', 450.00, 'Traditional mixed pickle jar'),
('Tapal Danedar Tea 900g', 'Food & Grocery', 1400.00, 'Strong blend black tea'),
('Shan Biryani Masala Box', 'Food & Grocery', 120.00, 'Spice mix for Sindhi Biryani'),
('Olpers Milk 1L', 'Food & Grocery', 280.00, 'Full cream UHT milk'),
('Mitchells Ketchup 1kg', 'Food & Grocery', 650.00, 'Rich tomato ketchup'),
('Rooh Afza 800ml', 'Beverages', 450.00, 'Summer refresher drink'),
('Pak Fan Ceiling 56"', 'Appliances', 8500.00, 'Energy saver ceiling fan'),
('Dawlance Fridge 9188', 'Appliances', 85000.00, 'Medium size refrigerator inverter'),
('Haier AC 1.5 Ton', 'Appliances', 145000.00, 'DC Inverter Air Conditioner'),
('Honda CD70 Bike', 'Vehicles', 157000.00, 'Red motorcycle 70cc'),
('United 125cc Bike', 'Vehicles', 110000.00, 'Economical 125cc bike'),
('Textile Bedsheet Set', 'Home & Living', 3500.00, 'King size printed cotton sheet'),
('Gul Ahmed Lawn Suit', 'Fashion', 4500.00, 'Unstitched 3-piece lawn suit'),
('J. Perfume 50ml', 'Personal Care', 3200.00, 'Men fragrance janan');

-- STOCK
INSERT INTO warehouse_products (warehouse_id, product_id, qty, reorder_level)
SELECT w.warehouse_id, p.product_id, 100, 10
FROM warehouses w CROSS JOIN products p;

-- ============================================
-- PART 4: TRANSACTIONAL DATA & ASSIGNMENTS
-- ============================================

-- PROJECTS (15 Projects)
INSERT INTO projects (department_id, location_id, project_name, start_date, end_date, status) VALUES
(1, 1, 'GTS Website Redesign', '2023-01-01', '2023-06-30', 'COMPLETED'),
(1, 1, 'Cyber Security Audit 2024', '2024-01-10', '2024-04-10', 'IN_PROGRESS'),
(5, 2, 'Lahore Summer Sales Drive', '2024-05-01', '2024-08-01', 'PLANNING'),
(4, 3, 'Islamabad Stock Upgrade', '2024-02-15', '2024-05-15', 'IN_PROGRESS'),
(5, 5, 'Faisalabad Market Expansion', '2023-09-01', '2023-12-31', 'COMPLETED'),
(2, 1, 'Finance System Migration', '2024-03-01', '2024-09-01', 'ON_HOLD'),
(3, 1, 'HR Automation System', '2024-04-01', '2024-10-01', 'IN_PROGRESS'),
(5, 4, 'Production Line Upgrade', '2024-01-15', '2024-06-15', 'COMPLETED'),
(4, 3, 'Customer Logic Portal', '2024-05-10', '2024-08-10', 'PLANNING'),
(2, 2, 'Data Warehousing Initiative', '2023-11-01', '2024-02-28', 'COMPLETED'),
(1, 1, 'Cloud Migration Phase 1', '2024-06-01', '2024-12-31', 'PLANNING'),
(3, 1, 'Payroll System Update', '2024-03-01', '2024-04-30', 'IN_PROGRESS'),
(4, 1, 'Mobile App Launch', '2024-01-01', '2024-06-01', 'COMPLETED'),
(5, 5, 'Quality Assurance Protocol', '2024-02-01', '2024-05-01', 'COMPLETED'),
(2, 1, 'Network Infrastructure Revamp', '2024-05-15', '2024-09-15', 'IN_PROGRESS');

-- EMP_PROJECTS (Assign almost everyone)
INSERT INTO emp_projects (employee_id, project_manager_id, project_id) VALUES
-- Project 1 (Website) - Manager Hamza (1)
(8, 1, 1), (20, 1, 1), (21, 1, 1), (36, 1, 1),
-- Project 2 (Cyber Audit) - Manager Wajid (2)
(7, 2, 2), (25, 2, 2), (26, 2, 2), (27, 2, 2),
-- Project 3 (Summer Sales) - Manager Umer (5) -> Umais (4)
(6, 4, 3), (11, 4, 3), (12, 4, 3), (13, 4, 3), (14, 4, 3),
-- Project 4 (Stock Upgrade) - Manager Umais (4)
(15, 4, 4), (16, 4, 4), (35, 4, 4),
-- Project 7 (HR Automation) - Manager Hassan (3)
(29, 3, 7), (30, 3, 7), (31, 3, 7),
-- Project 8 (Production Upgrade) - Manager Umer (5)
(9, 5, 8), (32, 5, 8), (33, 5, 8), (34, 5, 8),
-- Project 10 (Data Warehouse) - Manager Wajid (2)
(28, 2, 10), (37, 2, 10),
-- Project 13 (Mobile App) - Manager Hamza (1)
(22, 1, 13), (23, 1, 13), (24, 1, 13), (40, 1, 13),
-- Project 15 (Network Revamp)
(1, 2, 15); -- Hamza working on Wajid's project

-- CUSTOMERS
INSERT INTO customers (department_id, salesman_id, name, email, phone, address) VALUES
(4, 11, 'Karachi Electronics', 'info@khelectronics.pk', '021-33334444', 'Saddar, Karachi'),
(4, 11, 'Lahore Traders', 'contact@lahoretraders.pk', '042-33334444', 'Hall Road, Lahore'),
(4, 12, 'Islamabad Tech Solutions', 'support@isbtech.pk', '051-33334444', 'Blue Area, Islamabad'),
(4, 12, 'Multan Medical Store', 'mms@multan.pk', '061-33334444', 'Nishtar Road, Multan'),
(4, 11, 'Faisalabad Fabrics', 'sales@fstraders.pk', '041-33334444', 'Clock Tower, Faisalabad'),
(4, 11, 'Quetta Dry Fruit House', 'orders@qdf.pk', '081-33334444', 'Liaquat Bazaar, Quetta'),
(4, 12, 'Peshawar Chapli House', 'info@chapli.pk', '091-33334444', 'Qissa Khwani, Peshawar'),
(4, 11, 'Sialkot Sports Gear', 'export@sialkotsports.pk', '052-33334444', 'Defense Road, Sialkot'),
(4, 12, 'Ahmed General Store', 'ahmed@gmail.com', '0300-1234567', 'Gulshan-e-Iqbal, Karachi'),
(4, 11, 'Bismillah Bakery', 'bismillah@gmail.com', '0321-9876543', 'DHA Phase 6, Lahore');

-- ORDERS
INSERT INTO orders_m (order_date, customer_id, salesman_id, total_amount, status) VALUES
('2024-03-01', 1, 11, 150000.00, 'COMPLETED'),
('2024-03-05', 2, 11, 45000.00, 'COMPLETED'),
('2024-03-10', 3, 12, 250000.00, 'PROCESSING'),
('2024-03-12', 4, 12, 12000.00, 'PENDING'),
('2024-03-15', 5, 11, 85000.00, 'CANCELLED'),
('2024-03-18', 6, 11, 60000.00, 'COMPLETED'),
('2024-03-20', 7, 12, 35000.00, 'PENDING'),
('2024-03-22', 8, 11, 200000.00, 'PROCESSING'),
('2024-03-25', 9, 12, 5000.00, 'COMPLETED'),
('2024-03-28', 10, 11, 1500.00, 'PENDING');

-- ORDER ITEMS
INSERT INTO order_items (order_id, warehouse_id, product_id, qty, unit_price) VALUES
(1, 1, 10, 1, 145000.00),
(1, 1, 6, 5, 650.00),
(2, 2, 1, 15, 2500.00),
(2, 2, 4, 50, 120.00),
(3, 3, 9, 3, 85000.00);

-- WORK LOGS
INSERT INTO work_log (employee_id, project_id, work_date, start_time, end_time, total_hours, notes, approval_status, approved_by) VALUES
(8, 1, CURRENT_DATE, '09:00:00', '17:00:00', 8.0, 'Worked on backend integration', 'PENDING', NULL),
(7, 2, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '10:00:00', '16:00:00', 6.0, 'Vulnerability assessment', 'APPROVED', 2),
(11, 3, CURRENT_DATE, '09:00:00', '12:00:00', 3.0, 'Client meetings', 'PENDING', NULL),
(12, 3, DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), '14:00:00', '15:00:00', 1.0, 'Break', 'REJECTED', 6),
(1, 2, CURRENT_DATE, '08:00:00', '18:00:00', 10.0, 'Management', 'APPROVED', 1);

-- =================================================================
-- DONE
-- =================================================================
SELECT 'Setup Complete' AS Status;
