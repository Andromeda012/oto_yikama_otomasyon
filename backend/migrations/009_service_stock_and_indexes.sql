-- Phase 2: map service definitions to stock products consumed per completed job.
-- Run after 008_statistics_indexes.sql.

CREATE TABLE IF NOT EXISTS service_products (
  service_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity DECIMAL(12,3) NOT NULL,
  PRIMARY KEY (service_id, product_id),
  CONSTRAINT fk_service_products_service FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
  CONSTRAINT fk_service_products_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

