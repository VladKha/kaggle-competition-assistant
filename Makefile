make_virtualenv:
	@echo "Creating virtualenv..."
	python3 -m venv .venv							; \
	source .venv/bin/activate

install_dependencies:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements-dev.txt

start_opensearch:
	docker run -it \
	--rm \
    --name opensearch-node \
    -p 9200:9200 \
    -p 9600:9600 \
    -e OPENSEARCH_INITIAL_ADMIN_PASSWORD=My_super_password1 \
    -e "discovery.type=single-node"  \
    opensearchproject/opensearch:2.16.0

setup_env: make_virtualenv install_dependencies

up:
	docker compose --env-file .env up --build

down:
	docker compose down