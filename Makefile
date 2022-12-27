SHELL := /bin/bash

af: autoformat  ## Alias for `autoformat`
autoformat:  ## Run the autoformatter.
	isort --atomic --profile black  .
	black .

l: lint  ## Alias for `lint`
lint:  ## Run the linter.
	PYTHONPATH=. pylint --rcfile=.pylintrc  signal_bot