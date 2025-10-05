APP_NAME=app
IMAGE_NAME=etp_parsing:latest
UID?=1000

.PHONY: build run run-cron run-once stop logs

build:
	docker compose build --build-arg UID=$(UID)

run-cron:
	RUN_CRON=1 docker compose up -d $(APP_NAME)

run-once:
	RUN_CRON=0 docker compose up -d $(APP_NAME)

stop:
	docker compose down

logs:
	docker compose logs -f $(APP_NAME)
