all: run

run: clean fetch
	python parse_posts.py -p posts/ -o output/

parse: clean
	python parse_posts.py -p posts/ -o output/

fetch:
	cd posts/ && git pull

clean:
	rm -rf output/
