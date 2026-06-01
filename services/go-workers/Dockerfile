FROM golang:1.23 AS builder
WORKDIR /app
COPY go.mod .
COPY main.go .
RUN go build -o nox-go-workers .

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/nox-go-workers /usr/local/bin/nox-go-workers
CMD ["nox-go-workers"]
