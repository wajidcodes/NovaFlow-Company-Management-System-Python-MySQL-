-- =================================================================
-- ADD EXTRA PROJECTS & ASSIGNMENTS (UPDATE SCRIPT)
-- =================================================================
-- Run this script to add more projects and assign employees
-- WITHOUT deleting your existing data.
-- =================================================================

USE company_management;

-- 1. INSERT MORE PROJECTS
-- =================================================================
INSERT INTO projects (department_id, location_id, project_name, start_date, end_date, status) VALUES
(3, 1, 'HR Automation System', '2024-04-01', '2024-10-01', 'IN_PROGRESS'),
(5, 4, 'Production Line Upgrade', '2024-01-15', '2024-06-15', 'COMPLETED'),
(4, 3, 'Customer Logic Portal', '2024-05-10', '2024-08-10', 'PLANNING'),
(2, 2, 'Data Warehousing Initiative', '2023-11-01', '2024-02-28', 'COMPLETED'),
(1, 1, 'Cloud Migration Phase 1', '2024-06-01', '2024-12-31', 'PLANNING'),
(3, 1, 'Payroll System Update', '2024-03-01', '2024-04-30', 'IN_PROGRESS'),
(4, 1, 'Mobile App Launch', '2024-01-01', '2024-06-01', 'COMPLETED'),
(5, 5, 'Quality Assurance Protocol', '2024-02-01', '2024-05-01', 'COMPLETED'),
(2, 1, 'Network Infrastructure Revamp', '2024-05-15', '2024-09-15', 'IN_PROGRESS');

-- 2. ASSIGN GENERAL EMPLOYEES TO NEW PROJECTS
-- =================================================================
-- We use subqueries to handle IDs safely regardless of previous scripts

-- Assign all IT Dept General Employees to "Cloud Migration"
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 1, (SELECT project_id FROM projects WHERE project_name = 'Cloud Migration Phase 1' LIMIT 1)
FROM person p
WHERE p.department_id = 1 AND p.person_type = 'GENERAL_EMPLOYEE';

-- Assign all Accounts Dept General Employees to "HR Automation"
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 3, (SELECT project_id FROM projects WHERE project_name = 'HR Automation System' LIMIT 1)
FROM person p
WHERE p.department_id = 3 AND p.person_type = 'GENERAL_EMPLOYEE';

-- Assign all Production Dept General Employees to "Production Line Upgrade"
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 5, (SELECT project_id FROM projects WHERE project_name = 'Production Line Upgrade' LIMIT 1)
FROM person p
WHERE p.department_id = 5 AND p.person_type = 'GENERAL_EMPLOYEE';

-- Assign all Salesmen to "Customer Logic Portal"
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 4, (SELECT project_id FROM projects WHERE project_name = 'Customer Logic Portal' LIMIT 1)
FROM person p
WHERE p.person_type = 'SALESMAN';

-- Assign Cyber Security Employees to "Data Warehousing"
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 2, (SELECT project_id FROM projects WHERE project_name = 'Data Warehousing Initiative' LIMIT 1)
FROM person p
WHERE p.department_id = 2 AND p.person_type = 'GENERAL_EMPLOYEE';

-- Double Assignments (Busy Employees) - Assign some IT people to Mobile App too
INSERT INTO emp_projects (employee_id, project_manager_id, project_id)
SELECT p.person_id, 1, (SELECT project_id FROM projects WHERE project_name = 'Mobile App Launch' LIMIT 1)
FROM person p
WHERE p.department_id = 1 AND p.person_type = 'GENERAL_EMPLOYEE' LIMIT 3;

-- =================================================================
-- DONE: Check assignments
-- =================================================================
SELECT p.name, proj.project_name 
FROM emp_projects ep 
JOIN person p ON ep.employee_id = p.person_id 
JOIN projects proj ON ep.project_id = proj.project_id
ORDER BY proj.project_name;
