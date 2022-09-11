test:
	python -m unittest discover -p "*_test.py"

run:
	@bash -c "$$(cat config.env | xargs) python deye_main.py"

docker-build:
	@docker build -t deye-inverter-mqtt .

docker-run:
	@docker run --rm --env-file config.env deye-inverter-mqtt