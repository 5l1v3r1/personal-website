all: build_site

deploy: fetch_posts build_site
	cd output/ && git add . && git commit -m "Site regeneration" && git push

build_site: clean
	cp -r static/* output/
	python build_blog.py -p posts/ -o output/

fetch_posts:
	cd posts/ && git reset --hard && git pull

clean:
	rm -rf output/*
