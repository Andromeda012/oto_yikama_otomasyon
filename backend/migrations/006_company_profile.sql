CREATE TABLE IF NOT EXISTS company_profile (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(150) NOT NULL DEFAULT '',
    legal_name VARCHAR(200),
    tax_number VARCHAR(30),
    tax_office VARCHAR(120),
    phone VARCHAR(30),
    email VARCHAR(150),
    website VARCHAR(200),
    address VARCHAR(255),
    city VARCHAR(80),
    district VARCHAR(80)
);

INSERT INTO company_profile (id, company_name)
SELECT 1, ''
WHERE NOT EXISTS (SELECT 1 FROM company_profile WHERE id = 1);
