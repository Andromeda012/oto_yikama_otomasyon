-- Reporting indexes. Run after 007_system_settings.sql.
-- These improve date-range reporting and operational summaries.
CREATE INDEX idx_sales_created_status_vehicle ON sales (created_at, status, vehicle_job_id);
CREATE INDEX idx_appointments_start_status ON appointments (start_at, status);
CREATE INDEX idx_vehicle_jobs_created_status ON vehicle_jobs (created_at, status);
CREATE INDEX idx_vehicle_jobs_delivered_status ON vehicle_jobs (delivered_at, status);
CREATE INDEX idx_sale_items_sale_type ON sale_items (sale_id, line_type);
