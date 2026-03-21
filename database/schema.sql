CREATE DATABASE IF NOT EXISTS e_plastic_db;
USE e_plastic_db;

CREATE TABLE locations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  city VARCHAR(100),
  state VARCHAR(100)
);

CREATE TABLE plastic_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  recyclable BOOLEAN DEFAULT TRUE
);

CREATE TABLE waste_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  location_id INT,
  plastic_type_id INT,
  quantity_kg DECIMAL(10,2) NOT NULL,
  recorded_date DATE NOT NULL,
  recorded_by VARCHAR(100),
  FOREIGN KEY (location_id) REFERENCES locations(id),
  FOREIGN KEY (plastic_type_id) REFERENCES plastic_types(id)
);