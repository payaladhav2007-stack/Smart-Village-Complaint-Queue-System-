-- GS-504: PostgreSQL triggers for incremental resolution-time analytics
-- Run manually once per database via: psql -U gramsmart_user -d gramsmart_db -f db_triggers/resolution_summary_triggers.sql

CREATE TABLE IF NOT EXISTS resolution_time_summary (
    category_key VARCHAR(50) PRIMARY KEY,
    ticket_type VARCHAR(20) NOT NULL,
    total_completed INTEGER NOT NULL DEFAULT 0,
    avg_resolution_hours NUMERIC(10, 2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Grievance trigger: fires only on transition INTO 'resolved'
CREATE OR REPLACE FUNCTION update_complaint_resolution_summary()
RETURNS TRIGGER AS $$
DECLARE
    hours_taken NUMERIC;
BEGIN
    IF NEW.status = 'resolved' AND (OLD.status IS DISTINCT FROM 'resolved') THEN
        hours_taken := EXTRACT(EPOCH FROM (NEW.updated_at - NEW.created_at)) / 3600.0;

        INSERT INTO resolution_time_summary (category_key, ticket_type, total_completed, avg_resolution_hours, updated_at)
        VALUES (NEW.category, 'grievance', 1, hours_taken, now())
        ON CONFLICT (category_key) DO UPDATE SET
            avg_resolution_hours = (
                (resolution_time_summary.avg_resolution_hours * resolution_time_summary.total_completed) + hours_taken
            ) / (resolution_time_summary.total_completed + 1),
            total_completed = resolution_time_summary.total_completed + 1,
            updated_at = now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_complaint_resolution_summary ON grievances_complaint;
CREATE TRIGGER trg_complaint_resolution_summary
AFTER UPDATE ON grievances_complaint
FOR EACH ROW
EXECUTE FUNCTION update_complaint_resolution_summary();

-- Appointment trigger: fires only on transition INTO 'completed'
CREATE OR REPLACE FUNCTION update_appointment_resolution_summary()
RETURNS TRIGGER AS $$
DECLARE
    hours_taken NUMERIC;
BEGIN
    IF NEW.status = 'completed' AND (OLD.status IS DISTINCT FROM 'completed') THEN
        hours_taken := EXTRACT(EPOCH FROM (NEW.updated_at - NEW.created_at)) / 3600.0;

        INSERT INTO resolution_time_summary (category_key, ticket_type, total_completed, avg_resolution_hours, updated_at)
        VALUES (NEW.service_type, 'appointment', 1, hours_taken, now())
        ON CONFLICT (category_key) DO UPDATE SET
            avg_resolution_hours = (
                (resolution_time_summary.avg_resolution_hours * resolution_time_summary.total_completed) + hours_taken
            ) / (resolution_time_summary.total_completed + 1),
            total_completed = resolution_time_summary.total_completed + 1,
            updated_at = now();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_appointment_resolution_summary ON appointments_appointment;
CREATE TRIGGER trg_appointment_resolution_summary
AFTER UPDATE ON appointments_appointment
FOR EACH ROW
EXECUTE FUNCTION update_appointment_resolution_summary();