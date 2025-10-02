DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    user_type TEXT DEFAULT 'patient', -- patient, doctor, caregiver
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS assessments;
CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    wellness_score INTEGER NOT NULL,
    wellness_level TEXT NOT NULL,
    assessment_data TEXT NOT NULL, -- JSON string
    causal_analysis TEXT NOT NULL, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS mood_logs;
CREATE TABLE mood_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood TEXT NOT NULL, -- Happy, Neutral, Sad, Anxious
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS emergency_logs;
CREATE TABLE emergency_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    emergency_type TEXT NOT NULL,
    location_data TEXT, -- JSON string
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS doctor_patients;
CREATE TABLE doctor_patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    relationship TEXT DEFAULT 'primary_care',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES users (id),
    FOREIGN KEY (patient_id) REFERENCES users (id),
    UNIQUE(doctor_id, patient_id)
);

DROP TABLE IF EXISTS appointments;
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    appointment_type TEXT NOT NULL,
    preferred_date DATE NOT NULL,
    notes TEXT,
    status TEXT DEFAULT 'pending', -- pending, confirmed, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

DROP TABLE IF EXISTS health_metrics;
CREATE TABLE health_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    metric_type TEXT NOT NULL, -- weight, blood_pressure, memory_score, etc.
    metric_value REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default admin user (password: password123)
INSERT INTO users (username, password, email, user_type) VALUES
('admin', 'pbkdf2:sha256:600000$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8$LeehkU1BEoH4Km2u', 'admin@alzheimerapp.com', 'admin');

-- Insert sample patient
INSERT INTO users (username, password, email, user_type) VALUES
('patient1', 'pbkdf2:sha256:600000$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8$LeehkU1BEoH4Km2u', 'patient1@example.com', 'patient');

-- Insert sample doctor
INSERT INTO users (username, password, email, user_type) VALUES
('doctor1', 'pbkdf2:sha256:600000$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8$LeehkU1BEoH4Km2u', 'doctor1@alzheimerapp.com', 'doctor');
