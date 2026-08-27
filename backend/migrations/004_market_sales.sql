-- Market / POS sales and stock movement foundation.
-- Run after 003_sales_and_delivery.sql.

ALTER TABLE sales
  ADD COLUMN payment_method VARCHAR(30) NULL,
  ADD INDEX idx_sales_payment_method (payment_method);

CREATE TABLE IF NOT EXISTS stock_movements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  sale_id INT NULL,
  movement_type VARCHAR(30) NOT NULL,
  quantity DECIMAL(12,3) NOT NULL,
  stock_before DECIMAL(12,3) NOT NULL,
  stock_after DECIMAL(12,3) NOT NULL,
  description VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_stock_movements_product (product_id),
  INDEX idx_stock_movements_sale (sale_id),
  INDEX idx_stock_movements_created (created_at),
  CONSTRAINT fk_stock_movements_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
  CONSTRAINT fk_stock_movements_sale FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
