# Development environment
## Prerequisites
1. [pyenv](https://github.com/pyenv/pyenv)
2. [poetry](https://python-poetry.org/)
3. GNU make

## Setup the environment
```
make py-setup
make py-install-dependencies
```

## Activate python environment
```
poetry shell
```

## Git hooks
This project uses pre-commit git hook to automatically format and lint the code.
Commited code must have zero linting issues.

# Working with the code
## Testing and running locally
```
make test
```

Local run reads configuration from `config.env`

```
make run
```

# Building docker images
## For local use
```
make docker-build-local
```
## Run locally
```
make docker-run
```

# Pull request requirements
Each PR must:
1. Have a meaningful title
2. Be specific - add a single feature, fix a single bug
3. Have properly formatted code (use `make py-code-format`)
4. Have zero linter errors/warnings (use `make py-check-code`)
5. Have proper test coverage (tbd)