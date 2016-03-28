all: parse

run: clean fetch
	python parse_posts.py -p posts/ -o output/
	cd output/ && git add . && git commit -m "Site regeneration" && git push

parse: clean
	python parse_posts.py -p posts/ -o output/

fetch:
	cd posts/ && git pull

clean:
	rm -rf output/*
