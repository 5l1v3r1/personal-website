all: build_site

deploy: fetch_posts build_site
	cd output/ && git add . && git commit -m "Site regeneration" && git push

build_site: clean copy_static
	cd src/ && python build_blog.py -p ../posts/ -o ../output/

fetch_posts:
	cd posts/ && git reset --hard && git clean -fd && git pull

copy_static:
	cp -r src/static/* output/
	rsync -av --exclude '*.markdown' --exclude '.*' --exclude '_*' posts/ output/posts

clean:
	rm -rf output/*

serve:
	cd output/ && python3 -m http.server

open:
	open 'http://localhost:8000'
