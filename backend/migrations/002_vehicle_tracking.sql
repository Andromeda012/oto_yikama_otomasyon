-- Vehicle tracking / operational work orders
CREATE TABLE IF NOT EXISTS vehicle_jobs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id INT NULL,
  customer_id INT NOT NULL,
  vehicle_id INT NOT NULL,
  staff_id INT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'waiting',
  priority INT NOT NULL DEFAULT 0,
  check_in_at DATETIME NULL,
  started_at DATETIME NULL,
  estimated_end_at DATETIME NULL,
  ready_at DATETIME NULL,
  delivered_at DATETIME NULL,
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_vehicle_jobs_appointment (appointment_id),
  INDEX idx_vehicle_jobs_status (status),
  INDEX idx_vehicle_jobs_vehicle (vehicle_id),
  INDEX idx_vehicle_jobs_created (created_at),
  INDEX idx_vehicle_jobs_staff (staff_id),
  CONSTRAINT fk_vehicle_jobs_appointment FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
  CONSTRAINT fk_vehicle_jobs_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicle_jobs_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicle_jobs_staff FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vehicle_job_services (
  job_id INT NOT NULL,
  service_id INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  duration_minutes INT NOT NULL,
  PRIMARY KEY (job_id, service_id),
  CONSTRAINT fk_vehicle_job_services_job FOREIGN KEY (job_id) REFERENCES vehicle_jobs(id) ON DELETE CASCADE,
  CONSTRAINT fk_vehicle_job_services_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vehicle_job_status_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL,
  status VARCHAR(30) NOT NULL,
  note VARCHAR(255) NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_vehicle_job_history_job (job_id),
  INDEX idx_vehicle_job_history_changed (changed_at),
  CONSTRAINT fk_vehicle_job_history_job FOREIGN KEY (job_id) REFERENCES vehicle_jobs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
