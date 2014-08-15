build:
	docker build -t basenode .

run:
	docker run --rm=true -i -t basenode /bin/bash
