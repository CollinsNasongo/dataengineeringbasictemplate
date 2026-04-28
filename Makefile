.PHONY: up init restart rebuild reset logs down destroy ps metabase

# Start full stack
up:
	docker compose up -d

# Initialize Airflow DB
init:
	docker compose up airflow-init

# Restart core services (fast dev loop)
restart:
	docker compose restart airflow-scheduler airflow-dag-processor

# Rebuild containers (for dependency changes)
rebuild:
	docker compose down
	docker compose build
	docker compose up -d

# Full clean reset (destructive)
reset:
	docker compose down -v
	docker compose build --no-cache
	docker compose up airflow-init
	docker compose up -d

# Stop everything
down:
	docker compose down

# Destroy everything — removes all containers, volumes and images
destroy:
	docker compose down -v --remove-orphans --rmi all
	docker volume prune -f
	docker image prune -f

# View logs (pass service=xxx to override, e.g. make logs service=airflow-worker)
logs:
	docker compose logs -f $${service:-airflow-scheduler}

# Show running containers
ps:
	docker compose ps

# Open Metabase in browser
metabase:
	cmd /c start http://localhost:3000