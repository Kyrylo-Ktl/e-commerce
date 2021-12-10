include .env
export

up:
	docker-compose up -d --build

down:
	docker-compose exec web python manage.py clear_db
	docker-compose down

seed_db:
	docker-compose exec web python manage.py seed_db

clear_db:
	docker-compose exec web python manage.py clear_db

run-tests:
	python -m unittest discover -s tests -p 'test_*.py'

shop-logs:
	docker logs --tail 50 --follow --timestamps flask_shop

db-logs:
	docker logs --tail 50 --follow --timestamps db_flask_shop

access-db:
	docker-compose exec db psql --username=${POSTGRES_DB_USER} --dbname=${POSTGRES_DB_NAME}

shop-shell:
	docker exec -it flask_shop sh
