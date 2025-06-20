.PHONY: help install run clean docker-build docker-up docker-down nmap

help:
	@echo "Commandes disponibles :"
	@echo "  make install        Installe les dépendances Python et nmap"
	@echo "  make run            Lance l'API localement"
	@echo "  make docker-build   Construit l'image Docker"
	@echo "  make docker-up      Démarre l'API avec Docker Compose"
	@echo "  make docker-down    Arrête les conteneurs Docker Compose"
	@echo "  make clean          Supprime la base de données locale"
	@echo "  make nmap           Installe nmap (Linux uniquement, nécessite sudo)"

install: nmap
	pip install -r requirements.txt

run:
	python -m shieldcli.api

docker-build:
	docker build -t shieldcli-api .

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	rm -f reports.db

nmap:
	@echo "Installation de nmap (Linux uniquement, nécessite sudo)..."
	sudo apt-get update && sudo apt-get install -y nmap
