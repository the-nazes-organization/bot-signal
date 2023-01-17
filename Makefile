SHELL := /bin/bash

af: autoformat  ## Alias for `autoformat`
autoformat:  ## Run the autoformatter.
	isort --atomic --profile black  .
	black --line-length 88 --preview .

l: lint  ## Alias for `lint`
lint:  ## Run the linter.
	PYTHONPATH=. ruff --config ruff.toml app


t : test  ## Alias for `test`
test:
	PYTHONPATH=. pytest --cov=app --cov-config=.coveragerc app/test
