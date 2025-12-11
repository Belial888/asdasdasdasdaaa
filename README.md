### **pip install pymysql**
pip install flask mysql-connector-python
pip install selenium webdriver-manager

CREATE DATABASE IF NOT EXISTS pwd_appointment_system;
USE pwd_appointment_system;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'patient',
    pwd_id_number VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    appointment_date VARCHAR(20), 
    appointment_time VARCHAR(20),
    purpose TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
INSERT IGNORE INTO users (full_name, email, password_hash, role, pwd_id_number) VALUES ('System Admin', 'admin@pwd.gov', 'admin123', 'admin', 'ADMIN-01')
