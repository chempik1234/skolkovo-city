up:
	docker	compose -f ./docker/docker-compose.yaml up -d

upd:
	docker compose -f ./docker/docker-compose.yaml up -d --build

down:
	docker compose -f ./docker/docker-compose.yaml down

deldb:
	docker volume rm docker_postgres_data

freeze:
	 pip freeze > .\bot\requirements.txt
