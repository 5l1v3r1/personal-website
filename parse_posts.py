import sys
import mistune
import os

def parse_posts(folder):
    # Read all markdown files in the specified folder to a set with the filename
    # as key.
    markdown = mistune.Markdown()
    for dir_entry in os.listdir(folder):
        path = os.path.join(folder, dir_entry)
        filename, extension = os.path.splitext(dir_entry)
        if extension == '.markdown' and os.path.isfile(path):
            with open(path) as post:
                title = filename
                markdown_content = post.read()
                html_content = markdown(markdown_content)
                
                print title
                print html_content

if __name__ == '__main__':
    posts_folder = sys.argv[1]
    parse_posts(posts_folder)
