.PHONY: setup dev demo tail test clean

setup:        ## bootstrap env
	./scripts/bootstrap.sh

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
