-- Create schema for GDPR fines data
CREATE SCHEMA IF NOT EXISTS gdpr;

-- Create table for GDPR fines
CREATE TABLE IF NOT EXISTS gdpr.fines (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    authority VARCHAR(200),
    company VARCHAR(200) NOT NULL,
    amount NUMERIC(20, 2) NOT NULL,
    date DATE NOT NULL,
    controller_processor VARCHAR(50),
    article_violated VARCHAR(100),
    type_of_violation TEXT,
    source_url TEXT,
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on commonly queried fields
CREATE INDEX IF NOT EXISTS idx_fines_country ON gdpr.fines(country);
CREATE INDEX IF NOT EXISTS idx_fines_date ON gdpr.fines(date);
CREATE INDEX IF NOT EXISTS idx_fines_article ON gdpr.fines(article_violated);

-- Create table for countries
CREATE TABLE IF NOT EXISTS gdpr.countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(2) UNIQUE NOT NULL,
    region VARCHAR(100),
    eu_member BOOLEAN DEFAULT TRUE
);

-- Create view for fines analysis
CREATE OR REPLACE VIEW gdpr.fines_analysis AS
SELECT
    f.id,
    f.country,
    c.region,
    f.authority,
    f.company,
    f.amount,
    f.date,
    EXTRACT(YEAR FROM f.date) AS year,
    EXTRACT(MONTH FROM f.date) AS month,
    f.article_violated,
    f.type_of_violation,
    f.summary
FROM
    gdpr.fines f
LEFT JOIN
    gdpr.countries c ON f.country = c.name;

-- Create role for application
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password';
    END IF;
END
$$;

-- Grant privileges
GRANT USAGE ON SCHEMA gdpr TO app_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA gdpr TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA gdpr TO app_user;

-- Add some sample country data
INSERT INTO gdpr.countries (name, code, region, eu_member)
VALUES
    ('Spain', 'ES', 'Southern Europe', TRUE),
    ('Germany', 'DE', 'Central Europe', TRUE),
    ('France', 'FR', 'Western Europe', TRUE),
    ('Italy', 'IT', 'Southern Europe', TRUE),
    ('United Kingdom', 'GB', 'Northern Europe', FALSE),
    ('Netherlands', 'NL', 'Western Europe', TRUE),
    ('Ireland', 'IE', 'Northern Europe', TRUE),
    ('Belgium', 'BE', 'Western Europe', TRUE),
    ('Sweden', 'SE', 'Northern Europe', TRUE),
    ('Norway', 'NO', 'Northern Europe', FALSE)
ON CONFLICT (name) DO NOTHING;

-- Add a function to update the 'updated_at' timestamp
CREATE OR REPLACE FUNCTION gdpr.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to update the timestamp on record updates
CREATE TRIGGER update_fines_timestamp
BEFORE UPDATE ON gdpr.fines
FOR EACH ROW EXECUTE FUNCTION gdpr.update_timestamp(); 