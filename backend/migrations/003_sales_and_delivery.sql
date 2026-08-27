-- Financial foundation for completed vehicle jobs.
-- Run after 001_initial_schema.sql and 002_vehicle_tracking.sql.
-- This migration is intentionally separate from application startup.

ALTER TABLE sales
  ADD COLUMN vehicle_job_id INT NULL,
  ADD COLUMN payment_status VARCHAR(30) NOT NULL DEFAULT 'unpaid';

ALTER TABLE sales
  ADD UNIQUE KEY uq_sales_vehicle_job (vehicle_job_id),
  ADD INDEX idx_sales_payment_status (payment_status);

ALTER TABLE sales
  ADD CONSTRAINT fk_sales_vehicle_job
  FOREIGN KEY (vehicle_job_id) REFERENCES vehicle_jobs(id) ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS sale_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sale_id INT NOT NULL,
  line_type VARCHAR(20) NOT NULL,
  service_id INT NULL,
  product_id INT NULL,
  description VARCHAR(255) NOT NULL,
  quantity DECIMAL(12,3) NOT NULL DEFAULT 1,
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
  line_total DECIMAL(10,2) NOT NULL DEFAULT 0,
  INDEX idx_sale_items_sale (sale_id),
  INDEX idx_sale_items_service (service_id),
  INDEX idx_sale_items_product (product_id),
  CONSTRAINT fk_sale_items_sale FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
  CONSTRAINT fk_sale_items_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL,
  CONSTRAINT fk_sale_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE account_transactions
  ADD COLUMN sale_id INT NULL,
  ADD COLUMN vehicle_job_id INT NULL,
  ADD INDEX idx_account_transactions_sale (sale_id),
  ADD INDEX idx_account_transactions_vehicle_job (vehicle_job_id);

ALTER TABLE account_transactions
  ADD CONSTRAINT fk_account_transactions_sale
  FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL,
  ADD CONSTRAINT fk_account_transactions_vehicle_job
  FOREIGN KEY (vehicle_job_id) REFERENCES vehicle_jobs(id) ON DELETE SET NULL;
