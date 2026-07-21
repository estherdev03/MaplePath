pgup:
	docker compose -f docker-compose.dev.yaml up -d

pgdownvol:
	docker compose -f docker-compose.dev.yaml down -v

pgdown:
	docker compose -f docker-compose.dev.yaml down