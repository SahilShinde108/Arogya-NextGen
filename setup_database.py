import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect('health.db')
cursor = connection.cursor()

# --- Drop all existing tables to ensure a clean start ---
cursor.execute("DROP TABLE IF EXISTS readings")
cursor.execute("DROP TABLE IF EXISTS prescriptions")
cursor.execute("DROP TABLE IF EXISTS triage_reports")
cursor.execute("DROP TABLE IF EXISTS pharmacy_inventory")
cursor.execute("DROP TABLE IF EXISTS pharmacies")
cursor.execute("DROP TABLE IF EXISTS patients")

# --- Create Patients Table ---
cursor.execute('''
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone_number TEXT UNIQUE NOT NULL,
    email TEXT, password_hash TEXT NOT NULL, active_call_link TEXT, age INTEGER, gender TEXT,
    village TEXT, asha_worker_phone TEXT 
)''')

# --- Create Pharmacies & Inventory Tables ---
cursor.execute('''CREATE TABLE pharmacies (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, location TEXT)''')
cursor.execute('''
CREATE TABLE pharmacy_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pharmacy_id INTEGER, medication_name TEXT NOT NULL,
    stock_status TEXT NOT NULL, last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id)
)''')

# --- Create Prescriptions Table ---
cursor.execute('''
CREATE TABLE prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, medication_name TEXT NOT NULL,
    dosage TEXT, notes TEXT, is_active INTEGER DEFAULT 1, dispensing_pharmacy_id INTEGER, 
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (dispensing_pharmacy_id) REFERENCES pharmacies (id)
)''')

# --- Create Readings Table ---
cursor.execute('''
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, reading_type TEXT NOT NULL, 
    value1 INTEGER NOT NULL, value2 INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (patient_id) REFERENCES patients (id)
)''')

# --- Create Triage Reports Table (UPDATED SCHEMA) ---
cursor.execute('''
CREATE TABLE triage_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    patient_id INTEGER, 
    chief_complaint TEXT NOT NULL,
    symptoms TEXT, 
    notes TEXT, 
    ai_prediction TEXT, -- NEW COLUMN for AI output
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id)
)
''')

# --- Insert Sample Data ---
cursor.execute("INSERT INTO pharmacies (name, location) VALUES (?, ?)", ('Nabha Civil Hospital Pharmacy', 'Nabha City'))
cursor.execute("INSERT INTO pharmacies (name, location) VALUES (?, ?)", ('PHC Bhadson Pharmacy', 'Bhadson Village'))
cursor.execute("INSERT INTO pharmacy_inventory (pharmacy_id, medication_name, stock_status) VALUES (?, ?, ?)", (1, 'Paracetamol 500mg', 'In Stock'))
cursor.execute("INSERT INTO pharmacy_inventory (pharmacy_id, medication_name, stock_status) VALUES (?, ?, ?)", (1, 'Metformin 500mg', 'Out of Stock'))
cursor.execute("INSERT INTO pharmacy_inventory (pharmacy_id, medication_name, stock_status) VALUES (?, ?, ?)", (2, 'Metformin 500mg', 'In Stock'))

hashed_password = generate_password_hash('password123')
asha_phone = '+919123456789'
cursor.execute("INSERT INTO patients (name, phone_number, age, gender, village, password_hash, asha_worker_phone) VALUES (?, ?, ?, ?, ?, ?, ?)", 
    ('Ramesh Patil', '+919876543210', 65, 'Male', 'Songir', hashed_password, asha_phone))

connection.commit()
connection.close()
print("Database `health.db` was reset with the complete schema, including the new AI prediction column.")

