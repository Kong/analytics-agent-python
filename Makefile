install:
	python setup.py install

test: install
	python -m unittest -v test

clean:
	rm -rf mashape_analytics.egg-info build dist
	python setup.py clean


.PHONY: install test clean
