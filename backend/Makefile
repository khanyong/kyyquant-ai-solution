# Makefile for Auto Stock Backend

.PHONY: help build run stop clean logs test

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker image"
	@echo "  make run      - Run Docker container"
	@echo "  make stop     - Stop Docker container"
	@echo "  make clean    - Clean up containers and images"
	@echo "  make logs     - Show container logs"
	@echo "  make test     - Run tests"
	@echo "  make prod     - Build and run production"

build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

run:
	docker-compose up -d
	@echo "Server running at http://localhost:8000"

run-dev:
	docker-compose up

stop:
	docker-compose down

clean:
	docker-compose down -v
	docker rmi auto_stock_backend:latest || true

logs:
	docker-compose logs -f

test:
	docker-compose run backend pytest

prod:
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d

shell:
	docker-compose exec backend /bin/bash

restart:
	docker-compose restart

status:
	docker-compose ps