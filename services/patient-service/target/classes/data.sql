-- Sample data for development/testing
-- Patients
INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, primary_condition, conditions, insurance_plan, assigned_coordinator, created_at, updated_at)
VALUES
  ('P001', 'John', 'Doe', '1955-03-15', 'male', 'CKD', 'CKD,hypertension', 'Medicare Advantage', 'C001', NOW(), NOW()),
  ('P002', 'Jane', 'Smith', '1970-07-22', 'female', 'diabetes', 'diabetes', 'BlueCross PPO', 'C001', NOW(), NOW()),
  ('P003', 'Robert', 'Johnson', '1948-11-03', 'male', 'heart_failure', 'heart_failure,CKD,diabetes', 'Medicare Advantage', 'C002', NOW(), NOW()),
  ('P004', 'Mary', 'Williams', '1965-09-18', 'female', 'hypertension', 'hypertension', 'Aetna HMO', 'C002', NOW(), NOW()),
  ('P005', 'Carlos', 'Garcia', '1958-04-12', 'male', 'diabetes', 'diabetes,CKD', 'UnitedHealth', 'C001', NOW(), NOW())
;

-- Lab Results for P001 (CKD patient)
INSERT INTO lab_results (id, patient_id, test_name, result_value, unit, reference_range, is_abnormal, collected_date)
VALUES
  ('L001', 'P001', 'eGFR', 22.0, 'mL/min', '>60', true, '2024-10-15'),
  ('L002', 'P001', 'Potassium', 5.8, 'mEq/L', '3.5-5.0', true, '2024-10-15'),
  ('L003', 'P001', 'Creatinine', 3.1, 'mg/dL', '0.7-1.3', true, '2024-10-15'),
  ('L004', 'P001', 'Phosphorus', 5.2, 'mg/dL', '2.5-4.5', true, '2024-10-15'),
  ('L005', 'P001', 'Hemoglobin', 10.2, 'g/dL', '12-17.5', true, '2024-10-15'),
  ('L006', 'P001', 'BUN', 45.0, 'mg/dL', '7-20', true, '2024-10-15')
;

-- Lab Results for P002 (well-controlled diabetes)
INSERT INTO lab_results (id, patient_id, test_name, result_value, unit, reference_range, is_abnormal, collected_date)
VALUES
  ('L010', 'P002', 'HbA1c', 6.5, '%', '<7.0', false, '2024-10-10'),
  ('L011', 'P002', 'Fasting Glucose', 110.0, 'mg/dL', '70-100', true, '2024-10-10'),
  ('L012', 'P002', 'eGFR', 88.0, 'mL/min', '>60', false, '2024-10-10')
;

-- Lab Results for P003 (complex multi-morbidity)
INSERT INTO lab_results (id, patient_id, test_name, result_value, unit, reference_range, is_abnormal, collected_date)
VALUES
  ('L020', 'P003', 'BNP', 850.0, 'pg/mL', '<100', true, '2024-10-12'),
  ('L021', 'P003', 'eGFR', 35.0, 'mL/min', '>60', true, '2024-10-12'),
  ('L022', 'P003', 'HbA1c', 8.5, '%', '<7.0', true, '2024-10-12'),
  ('L023', 'P003', 'Potassium', 5.3, 'mEq/L', '3.5-5.0', true, '2024-10-12'),
  ('L024', 'P003', 'Creatinine', 2.1, 'mg/dL', '0.7-1.3', true, '2024-10-12')
;

-- Medications
INSERT INTO medications (id, patient_id, drug_name, dosage, frequency, prescriber, start_date, is_active)
VALUES
  ('M001', 'P001', 'Lisinopril', '20mg', 'daily', 'Dr. Smith', '2023-01-15', true),
  ('M002', 'P001', 'Amlodipine', '10mg', 'daily', 'Dr. Smith', '2023-01-15', true),
  ('M003', 'P001', 'Calcitriol', '0.25mcg', 'daily', 'Dr. Lee', '2024-06-01', true),
  ('M010', 'P002', 'Metformin', '1000mg', 'twice daily', 'Dr. Patel', '2022-03-10', true),
  ('M020', 'P003', 'Carvedilol', '25mg', 'twice daily', 'Dr. Kim', '2023-05-20', true),
  ('M021', 'P003', 'Furosemide', '40mg', 'daily', 'Dr. Kim', '2023-05-20', true),
  ('M022', 'P003', 'Lisinopril', '10mg', 'daily', 'Dr. Kim', '2023-05-20', true),
  ('M023', 'P003', 'Metformin', '500mg', 'twice daily', 'Dr. Patel', '2023-06-01', true),
  ('M040', 'P004', 'Amlodipine', '5mg', 'daily', 'Dr. Jones', '2023-09-01', true),
  ('M050', 'P005', 'Metformin', '1000mg', 'twice daily', 'Dr. Patel', '2022-08-15', true),
  ('M051', 'P005', 'Glipizide', '10mg', 'daily', 'Dr. Patel', '2023-11-01', true),
  ('M052', 'P005', 'Lisinopril', '20mg', 'daily', 'Dr. Smith', '2023-01-15', true)
;
