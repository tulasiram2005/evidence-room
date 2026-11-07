.PHONY: analysis test
analysis:
	python3 analysis.py
test:
	python3 -m unittest discover -s tests -v
