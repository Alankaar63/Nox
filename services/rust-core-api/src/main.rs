use axum::{
    extract::State,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{env, net::SocketAddr, sync::Arc};
use uuid::Uuid;

#[derive(Clone)]
struct AppState {
    cassandra_url: String,
    kafka_brokers: String,
    redis_url: String,
}

#[derive(Deserialize)]
struct WorkoutSet {
    user_id: String,
    session_id: Option<Uuid>,
    exercise_name: String,
    set_number: i32,
    weight_kg: f64,
    reps: i32,
    rpe: Option<f64>,
    notes: Option<String>,
}

#[derive(Serialize)]
struct Accepted {
    accepted: bool,
    event_id: Uuid,
    route: &'static str,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    let state = Arc::new(AppState {
        cassandra_url: env::var("CASSANDRA_URL").unwrap_or_else(|_| "localhost:9042".to_string()),
        kafka_brokers: env::var("KAFKA_BROKERS").unwrap_or_else(|_| "localhost:9092".to_string()),
        redis_url: env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379/0".to_string()),
    });

    let app = Router::new()
        .route("/health", get(health))
        .route("/workouts/set", post(log_workout_set))
        .route("/nutrition/log", post(accept_event))
        .route("/lock-in", post(accept_event))
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 8091));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health(State(state): State<Arc<AppState>>) -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "rust-core-api",
        "status": "ok",
        "cassandra": state.cassandra_url,
        "kafka": state.kafka_brokers,
        "redis": state.redis_url
    }))
}

async fn log_workout_set(Json(payload): Json<WorkoutSet>) -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "accepted": true,
        "event_id": Uuid::new_v4(),
        "route": "workouts.set.logged",
        "user_id": payload.user_id,
        "session_id": payload.session_id,
        "exercise": payload.exercise_name,
        "set_number": payload.set_number,
        "weight_kg": payload.weight_kg,
        "reps": payload.reps,
        "rpe": payload.rpe,
        "notes": payload.notes
    }))
}

async fn accept_event() -> Json<Accepted> {
    Json(Accepted {
        accepted: true,
        event_id: Uuid::new_v4(),
        route: "event.accepted",
    })
}
