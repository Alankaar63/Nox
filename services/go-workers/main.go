package main

import (
	"log"
	"os"
	"time"
)

func main() {
	kafka := getenv("KAFKA_BROKERS", "localhost:9092")
	influx := getenv("INFLUX_URL", "http://localhost:8086")
	log.Printf("NOX Go workers online. kafka=%s influx=%s", kafka, influx)

	for {
		log.Println("worker heartbeat: schedule-sync, notifications, biometric-rollups")
		time.Sleep(30 * time.Second)
	}
}

func getenv(key string, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}
