# =====================================
# 🌱 Project & Environment Configuration
# =====================================
# Read from pyproject.toml using grep (works on all platforms)
PROJECT_NAME = $(shell python3 -c "import re; print(re.search('name = \"(.*)\"', open('pyproject.toml').read()).group(1))")
VERSION = $(shell python3 -c "import re; print(re.search('version = \"(.*)\"', open('pyproject.toml').read()).group(1))")
-include .env
export

# Docker configuration
DOCKER_IMAGE = $(PROJECT_NAME):dev
CONTAINER_NAME = $(PROJECT_NAME)-app
PORT = 8080

# =====================================
# 🚀 Local Development
# =====================================
local: ## Run app locally
	uv run python main.py

# =====================================
# 📦 Windows Executable Build
# =====================================
build-exe: ## Build Windows executable (requires PyInstaller)
	@echo "Syncing dependencies..."
	uv sync
	@echo "Building Windows executable..."
	uv run python scripts/build_exe.py
	@echo "Build complete! Executable is in the 'dist' folder."

# =====================================
# 🐋 Docker (Development with hot reload)
# =====================================

build: ## Build development Docker image
	docker build --no-cache -t $(DOCKER_IMAGE) .
	@echo "✅ Docker image built: $(DOCKER_IMAGE)"

run: ## Run development container with hot reload
	docker run -d \
		--name $(CONTAINER_NAME)-dev \
		-p $(PORT):8080 \
		--env-file .env \
		-v $(CURDIR):/app \
		$(DOCKER_IMAGE) \
		uvicorn app:app --host 0.0.0.0 --port 8080 --reload
	@echo "🎯 App running at http://localhost:$(PORT) (hot reload)"

dev: build run ## Build and run development container with hot reload

ls: ## List files inside the dev image
	docker run --rm $(DOCKER_IMAGE) ls -la /app

stop: ## Stop dev container
	docker stop $(CONTAINER_NAME)-dev || true

clean: stop ## Stop and remove dev container and image
	docker rm $(CONTAINER_NAME)-dev || true
	docker rmi $(DOCKER_IMAGE) || true

restart: clean dev ## Restart dev container

# =======================
# 🪝 Hooks
# =======================

hooks:	## Install pre-commit on local machine
	pre-commit autoupdate && pre-commit install && pre-commit install --hook-type commit-msg

# Pre-commit ensures code quality before commits.
# Installing globally lets you use it across all projects.
# Check if pre-commit command exists : pre-commit --version


# =====================================
# ✨ Code Quality
# =====================================

lint:	## Run code linting and formatting
	uvx ruff check .
	uvx ruff format .

fix:	## Fix code issues and format
	uvx ruff check --fix .
	uvx ruff format .


# =======================
# 🔍 Security Scanning
# =======================
security-scan:		## Run all security checks
	gitleaks detect --source . --verbose && \
	uv export --no-dev -o requirements.txt && \
	uvx pip-audit -r requirements.txt && \
	python3 -c "import os; os.remove('requirements.txt') if os.path.exists('requirements.txt') else None" && \
	uvx bandit -r . --exclude ./.venv,./node_modules,./.git


# =====================================
# 📚 Documentation & Help
# =====================================

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@python3 -c "import re; lines=open('Makefile', encoding='utf-8').readlines(); targets=[re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$',l) for l in lines]; [print(f'  make {m.group(1):<20} {m.group(2)}') for m in targets if m]"


# =======================
# 🎯 PHONY Targets
# =======================

# Auto-generate PHONY targets (cross-platform)
.PHONY: $(shell python3 -c "import re; print(' '.join(re.findall(r'^([a-zA-Z_-]+):\s*.*?##', open('Makefile', encoding='utf-8').read(), re.MULTILINE)))")

# Test the PHONY generation
# test-phony:
# 	@echo "$(shell python3 -c "import re; print(' '.join(sorted(set(re.findall(r'^([a-zA-Z0-9_-]+):', open('Makefile', encoding='utf-8').read(), re.MULTILINE)))))")"
