all: run

run: clean
	python parse_posts.py -p posts/ -o output/

clean:
	rm -rf output/
