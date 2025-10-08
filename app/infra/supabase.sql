-- StopOdds Database Schema
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE age_bracket_enum AS ENUM ('18-24', '25-34', '35-44', '45+');
CREATE TYPE gender_enum AS ENUM ('Male', 'Female', 'Nonbinary', 'PreferNot');
CREATE TYPE ethnicity_enum AS ENUM (
    'Anglo Australian', 'Indigenous', 'South Asian', 'East Asian', 
    'Southeast Asian', 'Middle Eastern', 'African', 'European', 
    'Latin American', 'Other', 'PreferNot'
);
CREATE TYPE skin_tone_enum AS ENUM ('Light', 'Medium', 'Dark', 'PreferNot');
CREATE TYPE height_bracket_enum AS ENUM ('<160', '160-175', '175-190', '>190');
CREATE TYPE model_type_enum AS ENUM ('poisson', 'negbin', 'lightgbm');

-- Main submissions table
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    age_bracket age_bracket_enum,
    gender gender_enum,
    ethnicity ethnicity_enum,
    skin_tone skin_tone_enum,
    height_bracket height_bracket_enum,
    visible_disability BOOLEAN,
    concession BOOLEAN,
    trips INTEGER NOT NULL CHECK (trips >= 1 AND trips <= 200),
    stops INTEGER NOT NULL CHECK (stops >= 0),
    user_agent_hash TEXT,
    CONSTRAINT stops_not_exceed_trips CHECK (stops <= trips)
);

-- Model runs tracking
CREATE TABLE model_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    model_type model_type_enum NOT NULL,
    train_rows INTEGER NOT NULL,
    metrics JSONB,
    coeffs JSONB,
    public_snapshot BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Public aggregates (k-anonymized)
CREATE TABLE aggregates_public (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_key TEXT NOT NULL,
    n_people INTEGER NOT NULL CHECK (n_people >= 50), -- k-anonymity constraint
    n_trips INTEGER NOT NULL,
    n_stops INTEGER NOT NULL,
    rate_per_100 FLOAT NOT NULL,
    irr_vs_ref FLOAT,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,
    model_run_id UUID REFERENCES model_runs(run_id)
);

-- Indexes for performance
CREATE INDEX idx_submissions_created_at ON submissions(created_at);
CREATE INDEX idx_submissions_traits ON submissions(age_bracket, gender, ethnicity, skin_tone);
CREATE INDEX idx_model_runs_created_at ON model_runs(created_at);
CREATE INDEX idx_model_runs_public ON model_runs(public_snapshot);
CREATE INDEX idx_aggregates_group_key ON aggregates_public(group_key);
CREATE INDEX idx_aggregates_model_run ON aggregates_public(model_run_id);

-- Row Level Security (RLS)
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE aggregates_public ENABLE ROW LEVEL SECURITY;

-- Policies for public read access to aggregates
CREATE POLICY "Public read access to aggregates" ON aggregates_public
    FOR SELECT USING (true);

-- Policies for model runs (public snapshots only)
CREATE POLICY "Public read access to public model runs" ON model_runs
    FOR SELECT USING (public_snapshot = true);

-- Function to safely hash user agents with daily salt
CREATE OR REPLACE FUNCTION hash_user_agent(user_agent TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Use date as salt to rotate hashes daily
    RETURN encode(digest(user_agent || CURRENT_DATE::TEXT || 'stopodds_salt', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Function to calculate stop rate per 100 trips
CREATE OR REPLACE FUNCTION calculate_rate_per_100(stops INTEGER, trips INTEGER)
RETURNS FLOAT AS $$
BEGIN
    IF trips = 0 THEN
        RETURN 0;
    END IF;
    RETURN (stops::FLOAT / trips::FLOAT) * 100;
END;
$$ LANGUAGE plpgsql;

-- Function to check minimum sample size before enabling features
CREATE OR REPLACE FUNCTION check_minimum_sample()
RETURNS TABLE(
    total_submissions INTEGER,
    total_stops INTEGER,
    meets_minimum BOOLEAN
) AS $$
DECLARE
    min_submissions INTEGER := 500;
    min_stops INTEGER := 100;
    sub_count INTEGER;
    stop_count INTEGER;
BEGIN
    SELECT COUNT(*), COALESCE(SUM(stops), 0) 
    INTO sub_count, stop_count 
    FROM submissions;
    
    RETURN QUERY SELECT 
        sub_count,
        stop_count,
        (sub_count >= min_submissions AND stop_count >= min_stops);
END;
$$ LANGUAGE plpgsql;

-- Create a view for basic public statistics
CREATE OR REPLACE VIEW public_stats AS
SELECT 
    COUNT(*) as total_submissions,
    SUM(trips) as total_trips,
    SUM(stops) as total_stops,
    AVG(calculate_rate_per_100(stops, trips)) as avg_rate_per_100,
    MIN(created_at) as first_submission,
    MAX(created_at) as last_submission
FROM submissions;

-- Grant permissions for public access
GRANT SELECT ON public_stats TO anon, authenticated;
GRANT SELECT ON aggregates_public TO anon, authenticated;
GRANT SELECT ON model_runs TO anon, authenticated;

-- Comments for documentation
COMMENT ON TABLE submissions IS 'Anonymous submissions of trip and stop counts with demographic traits';
COMMENT ON TABLE model_runs IS 'Model training runs with metrics and coefficients';
COMMENT ON TABLE aggregates_public IS 'K-anonymized public aggregates for display (k>=50)';
COMMENT ON COLUMN submissions.user_agent_hash IS 'Daily-salted hash of user agent for basic fraud detection';
COMMENT ON COLUMN aggregates_public.n_people IS 'Number of people in group (must be >=50 for k-anonymity)';

-- Sample data insertion function for testing
CREATE OR REPLACE FUNCTION insert_sample_data()
RETURNS VOID AS $$
BEGIN
    -- This is for development/testing only
    INSERT INTO submissions (age_bracket, gender, ethnicity, skin_tone, height_bracket, visible_disability, concession, trips, stops)
    VALUES 
        ('25-34', 'Male', 'Anglo Australian', 'Light', '175-190', false, false, 20, 1),
        ('35-44', 'Female', 'South Asian', 'Medium', '160-175', false, true, 25, 2),
        ('18-24', 'Nonbinary', 'East Asian', 'Light', '<160', false, true, 15, 0),
        ('45+', 'Male', 'Indigenous', 'Dark', '>190', true, true, 30, 3);
    
    RAISE NOTICE 'Sample data inserted successfully';
END;
$$ LANGUAGE plpgsql;