
.PHONY: setup dev demo tail test clean prune-deps mongo-up dev-up

dev:          ## start dev server
demo:         ## send demo detections
tail:         ## tail tracks
test:         ## run tests

setup:        ## bootstrap env
	./scripts/bootstrap.sh

prune-deps:   ## Remove unused dependencies and check for issues (keeps uv.lock minimal)
	uv pip prune
	uv pip check

mongo-up:     ## Start MongoDB for development using Docker Compose
	docker compose -f docker-compose.mongo.yml --env-file .env up -d

dev:          ## start dev server
	. .venv/bin/activate && aura-cli dev-server

demo:         ## send demo detections
	. .venv/bin/activate && aura-cli detections-send scripts/demo.jsonl

tail:         ## tail tracks
	. .venv/bin/activate && aura-cli tracks-tail

test:         ## run tests
	. .venv/bin/activate && python -m pytest -q

clean:        ## nuke env and caches
	rm -rf .venv uv.lock aura_v2.egg-info && rm -rf "$$HOME/.cache/uv/builds-v0"

# All-in-one target for onboarding and dev setup
dev-up: setup prune-deps mongo-up
	@echo "Environment bootstrapped, dependencies pruned, and MongoDB started."
	@echo "Next: activate your venv and run 'make dev' or other targets as needed."
