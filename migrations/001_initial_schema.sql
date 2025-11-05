-- Migration: Initial Schema for LLM Lab
-- Database: Supabase (PostgreSQL)
-- Description: Creates all tables and relationships for the LLM Lab application

-- Create experiments table
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    prompt TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create index on experiments for faster queries
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON experiments(created_at);

-- Create responses table
CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    top_p DOUBLE PRECISION NOT NULL,
    max_tokens INTEGER DEFAULT 1000,
    text TEXT NOT NULL,
    finish_reason VARCHAR(50),
    validation_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_responses_experiment 
        FOREIGN KEY (experiment_id) 
        REFERENCES experiments(id) 
        ON DELETE CASCADE
);

-- Create indexes on responses table
CREATE INDEX IF NOT EXISTS idx_responses_experiment_id ON responses(experiment_id);
CREATE INDEX IF NOT EXISTS idx_responses_created_at ON responses(created_at);
CREATE INDEX IF NOT EXISTS idx_responses_temperature ON responses(temperature);
CREATE INDEX IF NOT EXISTS idx_responses_top_p ON responses(top_p);

-- Create metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    response_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_metrics_response 
        FOREIGN KEY (response_id) 
        REFERENCES responses(id) 
        ON DELETE CASCADE
);

-- Create indexes on metrics table
CREATE INDEX IF NOT EXISTS idx_metrics_response_id ON metrics(response_id);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name);
CREATE INDEX IF NOT EXISTS idx_metrics_value ON metrics(value);

-- Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_metrics_response_name ON metrics(response_id, name);

-- Create function to update updated_at timestamp (for experiments table)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_experiments_updated_at ON experiments;
CREATE TRIGGER update_experiments_updated_at
    BEFORE UPDATE ON experiments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

