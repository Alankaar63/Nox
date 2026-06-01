FROM rust:1.83 AS builder
WORKDIR /app
COPY Cargo.toml .
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/nox-rust-core-api /usr/local/bin/nox-rust-core-api
EXPOSE 8091
CMD ["nox-rust-core-api"]
