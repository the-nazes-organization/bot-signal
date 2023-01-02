SHELL := /bin/bash

af: autoformat  ## Alias for `autoformat`
autoformat:  ## Run the autoformatter.
	isort --atomic --profile black  .
	black --line-length 85 --experimental-string-processing .

l: lint  ## Alias for `lint`
lint:  ## Run the linter.
	PYTHONPATH=. python -m pylint --rcfile=.pylintrc  signal_bot