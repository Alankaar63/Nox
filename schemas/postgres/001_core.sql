CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS foods (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    serving_g NUMERIC NOT NULL DEFAULT 100,
    protein_g NUMERIC NOT NULL DEFAULT 0,
    carbs_g NUMERIC NOT NULL DEFAULT 0,
    fat_g NUMERIC NOT NULL DEFAULT 0,
    calories NUMERIC NOT NULL DEFAULT 0,
    diet_tags TEXT[] NOT NULL DEFAULT '{}',
    embedding vector(768)
);

CREATE TABLE IF NOT EXISTS exercises (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    movement_pattern TEXT NOT NULL,
    primary_muscles TEXT[] NOT NULL,
    equipment TEXT[] NOT NULL DEFAULT '{}',
    difficulty TEXT NOT NULL DEFAULT 'intermediate',
    rest_seconds_min INTEGER NOT NULL DEFAULT 60,
    rest_seconds_max INTEGER NOT NULL DEFAULT 180,
    embedding vector(768)
);

CREATE TABLE IF NOT EXISTS split_templates (
    id BIGSERIAL PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    philosophy TEXT NOT NULL,
    days JSONB NOT NULL,
    progression_rules JSONB NOT NULL DEFAULT '{}',
    embedding vector(768)
);

CREATE TABLE IF NOT EXISTS coach_articles (
    id BIGSERIAL PRIMARY KEY,
    coach TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    tags TEXT[] NOT NULL DEFAULT '{}',
    embedding vector(768)
);

CREATE INDEX IF NOT EXISTS foods_embedding_hnsw
ON foods USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS exercises_embedding_hnsw
ON exercises USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS coach_articles_embedding_hnsw
ON coach_articles USING hnsw (embedding vector_cosine_ops);
