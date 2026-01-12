# --------------------------------------
# Project variables
# --------------------------------------
PROJECT_NAME=let_me_learn_eng
# Get the absolute path of the directory containing the Makefile
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

ENV_FILE=$(ROOT_DIR)/.env
DOCKER_COMPOSE=$(ROOT_DIR)/docker/docker-compose.yml
WEB_SERVICE=web

# Base command to ensure paths are always resolved correctly
COMPOSE_CMD=docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE) --project-directory $(ROOT_DIR)

# --------------------------------------
# Docker Commands
# --------------------------------------

# Build Docker images
build:
	$(COMPOSE_CMD) build

# Start services
up:
	$(COMPOSE_CMD) up -d

# Stop services
down:
	$(COMPOSE_CMD) down

# Restart
restart: down up

# Logs
logs:
	$(COMPOSE_CMD) logs -f

# Shell
shell:
	$(COMPOSE_CMD) exec $(WEB_SERVICE) sh

# Rebuild and start
up-build:
	$(COMPOSE_CMD) up -d --build

# --------------------------------------
# Django Commands
# --------------------------------------

migrations:
	$(COMPOSE_CMD) exec $(WEB_SERVICE) python manage.py makemigrations

migrate:
	$(COMPOSE_CMD) exec $(WEB_SERVICE) python manage.py migrate

createsuperuser:
	$(COMPOSE_CMD) exec $(WEB_SERVICE) python manage.py createsuperuser

collectstatic:
	$(COMPOSE_CMD) exec $(WEB_SERVICE) python manage.py collectstatic --noinput