test:
	python -m unittest discover -p "*_test.py"

run:
	@bash -c "$$(cat config.env | xargs) python deye_main.py"
