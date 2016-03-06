# Blog engine

A blog engine that parses posts from Markdown files and spits out static html.

## How to use

The script `parse_posts.py` takes two arguments:

* A folder to look for posts in (`-p, --posts`)
* A folder to output html to (`-o, --output`)

Running the script will parse all markdown files in the posts folder and output ready-to-use html in the output folder.

## Dependencies

Uses Python 3.5.1. Install dependencies with:

    pip install -r requirements.txt
