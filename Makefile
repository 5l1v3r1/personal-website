all: build_site

deploy: fetch_posts build_site
	cd output/ && git add . && git commit -m "Site regeneration" && git push

build_site: clean copy_static
	python build_blog.py -p posts/ -o output/

fetch_posts:
	cd posts/ && git reset --hard && git pull

copy_static:
	cp -r static/* output/
	rsync -av --exclude '*.markdown' --exclude '.*' posts/ output/posts

clean:
	rm -rf output/*

server:
	cd output/ && python3 -m http.server
