GITHUB_USER = kbialek
VERSION = 2022.10.1

# Gets Github personal token from Bitwarden vault
get_github_token = \
	$(shell bw --session "$$(bw-read-session)" get item aa3dab0a-6c68-49d1-8a4d-193f37d3a5fc |\
		jq -r '.fields[] | select(.name=="token") | .value')

test:
	python -m unittest discover -p "*_test.py"

run:
	@bash -c "$$(cat config.env | xargs) python deye_docker_entrypoint.py"

docker-build-local:
	@docker buildx build \
		--platform linux/amd64 \
		--output type=docker \
		-t deye-inverter-mqtt:$(VERSION) .

docker-run:
	@docker run --rm --env-file config.env deye-inverter-mqtt

docker-push:
	@echo $(call get_github_token) | docker login ghcr.io -u $(GITHUB_USER) --password-stdin
	@docker buildx create --use
	@docker buildx build \
		--platform linux/amd64,linux/arm/v7 \
		--push \
		-t ghcr.io/$(GITHUB_USER)/deye-inverter-mqtt:$(VERSION) \
		.
	@docker buildx rm --all-inactive --force