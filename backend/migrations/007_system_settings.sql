CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Europe/Istanbul',
    currency VARCHAR(10) NOT NULL DEFAULT 'TRY',
    appointment_slot_minutes INT NOT NULL DEFAULT 30,
    appointment_advance_days INT NOT NULL DEFAULT 30,
    appointment_allow_past BOOLEAN NOT NULL DEFAULT FALSE,
    appointment_auto_job BOOLEAN NOT NULL DEFAULT TRUE,
    reminder_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    reminder_hours_before INT NOT NULL DEFAULT 24,
    sms_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    sms_provider VARCHAR(50) DEFAULT '',
    sms_sender VARCHAR(50) DEFAULT '',
    whatsapp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    whatsapp_provider VARCHAR(50) DEFAULT '',
    whatsapp_phone VARCHAR(30) DEFAULT '',
    business_hours TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO system_settings (business_hours)
SELECT '{"monday":{"enabled":true,"open":"08:00","close":"19:00"},"tuesday":{"enabled":true,"open":"08:00","close":"19:00"},"wednesday":{"enabled":true,"open":"08:00","close":"19:00"},"thursday":{"enabled":true,"open":"08:00","close":"19:00"},"friday":{"enabled":true,"open":"08:00","close":"19:00"},"saturday":{"enabled":true,"open":"09:00","close":"18:00"},"sunday":{"enabled":false,"open":"09:00","close":"17:00"}}'
WHERE NOT EXISTS (SELECT 1 FROM system_settings);
