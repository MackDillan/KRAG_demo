MODEL_DIR=models
MODEL_URL=https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q5_K_M.gguf
MODEL_FILE=$(MODEL_DIR)/mistral-7b-v0.1.Q5_K_M.gguf
VENV_DIR=venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip

# Entry point
all: venv download-model up-neo4j seed-db
	@echo "Project is ready to use."

# Creating a virtual environment and installing dependencies
venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed in venv"

# Add a new target to run seed_db.py
seed-db:
	@echo "Running seed_db.py in virtual environment..."
	$(PYTHON) seed_db.py
	@echo "seed_db.py executed"

# Downloading the model
download-model:
	mkdir -p $(MODEL_DIR)
	if [ ! -f $(MODEL_FILE) ]; then \
		echo "Downloading model..."; \
		curl -L $(MODEL_URL) -o $(MODEL_FILE); \
	else \
		echo "Model already exists: $(MODEL_FILE)"; \
	fi

# Starting Neo4j
up-neo4j:
	docker compose up -d
	@echo "Neo4j started: http://localhost:7474 (neo4j / neo4jneo4j)"

# Stopping all services
down:
	docker compose down

.PHONY: all venv download-model up-neo4j down
