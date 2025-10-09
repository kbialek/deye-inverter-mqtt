GITHUB_USER = kbialek
VERSION = $(shell grep "^version" pyproject.toml | head -1 | sed 's/version.=.//' | tr -d '"')

ARCHS = linux/amd64 linux/arm/v6 linux/arm/v7 linux/arm64/v8
DOCKER_BASE_IMAGE_TAG = 3.10.13-alpine3.18

null =
space = $(null) $(null)
comma = ,

# Gets Github personal token from Bitwarden vault
get_github_token = \
	$(shell BW_SESSION="$$(bw-read-session)" bw get item aa3dab0a-6c68-49d1-8a4d-193f37d3a5fc |\
		jq -r '.fields[] | select(.name=="token") | .value')

gen-tls-certs:
	@mkdir -p certs
	@tools/setup_certs.sh

mosquitto-start:
	@mosquitto -c mosquitto/mosquitto.conf -d

mosquitto-start-tls:
	@mosquitto -c mosquitto/mosquitto-tls.conf -d

mosquitto-stop:
	@pkill mosquitto

test:
	@uv run pytest -v --cov --cov-report=xml --log-cli-level=DEBUG

test-coverage: test
	@uv run coverage report --skip-empty --no-skip-covered --sort=Cover

test-mqtt: gen-tls-certs
	-@uv run pytest -v tests/deye_mqtt_inttest.py
	@rm certs/* && rmdir certs

test-at-connector:
	@bash -c "set -a; source config.env; uv run pytest -v --log-cli-level=DEBUG tests/deye_at_connector_inttest.py"

run:
	@uv run ./local-run.sh "python:$(DOCKER_BASE_IMAGE_TAG)"

$(ARCHS:%=docker-build-%): docker-build-%: py-export-requirements
	-@docker buildx rm deye-docker-build
	@docker buildx create --use --name deye-docker-build
	@docker buildx build \
		--build-arg base_image_tag=$(DOCKER_BASE_IMAGE_TAG) \
		--platform $* \
		--output type=docker \
		-t deye-inverter-mqtt:$(VERSION) \
		-t deye-inverter-mqtt:latest \
		.
	@docker buildx rm deye-docker-build

docker-build-local: docker-build-linux/amd64

docker-run:
	@docker run --rm \
		--net host \
		--env-file config.env \
		--volume ./certs:/opt/deye_inverter_mqtt/certs:ro \
		--volume ./plugins:/opt/deye_inverter_mqtt/plugins:ro \
		deye-inverter-mqtt

docker-shell:
	@docker run --rm \
		--net host \
		--env-file config.env \
		--volume ./certs:/opt/deye_inverter_mqtt/certs:ro \
		--entrypoint /bin/sh -ti \
		deye-inverter-mqtt

docker-push: test py-export-requirements
	@echo $(call get_github_token) | docker login ghcr.io -u $(GITHUB_USER) --password-stdin
	-@docker buildx rm deye-docker-build
	@docker buildx create --use --name deye-docker-build
	@docker --debug buildx build \
		--build-arg base_image_tag=$(DOCKER_BASE_IMAGE_TAG) \
		--platform $(subst $(space),$(comma),$(ARCHS)) \
		--push \
		-t ghcr.io/$(GITHUB_USER)/deye-inverter-mqtt:$(VERSION) \
		-t ghcr.io/$(GITHUB_USER)/deye-inverter-mqtt:latest \
		.
	@docker buildx rm deye-docker-build

docker-push-beta: test py-export-requirements
	@echo $(call get_github_token) | docker login ghcr.io -u $(GITHUB_USER) --password-stdin
	-@docker buildx rm deye-docker-build
	@docker buildx create --use --name deye-docker-build
	@docker buildx build \
		--build-arg base_image_tag=$(DOCKER_BASE_IMAGE_TAG) \
		--platform $(subst $(space),$(comma),$(ARCHS)) \
		--push \
		-t ghcr.io/$(GITHUB_USER)/deye-inverter-mqtt:$(VERSION) \
		.
	@docker buildx rm deye-docker-build

METRIC_GROUPS = \
	string \
	micro \
	deye_sg04lp3 \
	deye_sg04lp3_battery \
	deye_sg04lp3_ups \
	deye_sg04lp3_timeofuse \
	deye_sg04lp3_generator \
	igen_dtsd422 \
	deye_hybrid \
	deye_hybrid_battery \
	deye_hybrid_bms \
	deye_hybrid_timeofuse \
	deye_sg03lp1 \
	deye_sg02lp1 \
	deye_sg02lp1_battery \
	deye_sg02lp1_bms \
	deye_sg02lp1_timeofuse \
	settings \
	settings_micro \
	deye_sg01hp3 \
	deye_sg01hp3_battery \
	deye_sg01hp3_ups \
	deye_sg01hp3_bms \
	deye_sg01hp3_timeofuse \
	aggregated
GENERATE_DOCS_TARGETS = $(addprefix generate-docs-, $(METRIC_GROUPS))
$(GENERATE_DOCS_TARGETS): generate-docs-%:
	@mkdir -p docs
	@cd tools && python metric_group_doc_gen.py --group-name=$* > ../docs/metric_group_$*.md

generate-all-docs: $(GENERATE_DOCS_TARGETS)

git-install-hooks:
	@cp tools/git/pre-commit .git/hooks/

git-uninstall-hooks:
	@rm .git/hooks/pre-commit

py-setup: git-install-hooks
	uv python install
	uv venv

py-install-dependencies:
	uv run uv lock
	uv run uv sync

py-export-requirements:
	uv export --no-editable --no-emit-project --format requirements.txt --no-dev > requirements.txt
	uv export --no-editable --no-emit-project --format requirements.txt --only-dev > requirements-dev.txt

py-show-dependencies:
	uv tree

py-show-dependencies-outdated:
	uv run uv pip list --outdated

py-code-format:
	uv run black src/
	uv run black tests/

py-check-code:
	uv run flake8 src/
