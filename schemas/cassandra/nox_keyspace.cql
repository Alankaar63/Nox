CREATE KEYSPACE IF NOT EXISTS nox
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE nox;

CREATE TABLE IF NOT EXISTS workout_sessions_by_user_week (
    user_id text,
    week_bucket text,
    session_id uuid,
    session_date date,
    session_type text,
    start_time timestamp,
    end_time timestamp,
    total_volume_kg double,
    total_sets int,
    status text,
    notes text,
    PRIMARY KEY ((user_id, week_bucket), session_date, session_id)
) WITH CLUSTERING ORDER BY (session_date DESC, session_id DESC);

CREATE TABLE IF NOT EXISTS exercise_logs_by_session (
    user_id text,
    session_id uuid,
    set_number int,
    exercise_name text,
    weight_kg double,
    reps int,
    rpe double,
    notes text,
    logged_at timestamp,
    PRIMARY KEY ((user_id, session_id), set_number, exercise_name)
);

CREATE TABLE IF NOT EXISTS nutrition_logs_by_user_day (
    user_id text,
    log_date date,
    logged_at timestamp,
    meal_label text,
    food_name text,
    quantity_g double,
    protein_g double,
    carbs_g double,
    fat_g double,
    calories double,
    PRIMARY KEY ((user_id, log_date), logged_at)
) WITH CLUSTERING ORDER BY (logged_at DESC);

CREATE TABLE IF NOT EXISTS lock_ins_by_user_week (
    user_id text,
    week_bucket text,
    lock_in_id uuid,
    scheduled_date date,
    scheduled_time text,
    session_type text,
    duration_min int,
    recurring_pattern text,
    status text,
    notes text,
    PRIMARY KEY ((user_id, week_bucket), scheduled_date, scheduled_time, lock_in_id)
);
