include .env
export

up:
	docker-compose up -d --build

down:
	docker-compose down

shop-logs:
	docker logs --tail 50 --follow --timestamps flask_shop

db-logs:
	docker logs --tail 50 --follow --timestamps db_flask_shop

access-db:
	docker-compose exec db psql --username=${POSTGRES_USER} --dbname=${POSTGRES_DB}

shop-shell:
	docker exec -it flask_shop sh
