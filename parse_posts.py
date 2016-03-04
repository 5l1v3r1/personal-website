import sys
import mistune
import os
import getopt

def main(argv):
    posts_folder, output_folder = parse_arguments(argv)
    parse_posts(posts_folder, output_folder)

def parse_arguments(argv):
    try:
        opts, args = getopt.getopt(argv, 'hp:o:', ['help', 'posts=', 'output='])
    except getopt.GetoptError:
        invalid_arguments()

    posts = ''
    output = ''

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage_instructions()
            sys.exit()
        elif opt in ('-p', '--posts'):
            posts = arg
        elif opt in ('-o', '--output'):
            output = arg

    if posts == '' or output == '':
        invalid_arguments()

    return (posts, output)

def invalid_arguments():
    print_usage_instructions()
    sys.exit(2) # Exit code 2 = command line syntax error

def print_usage_instructions():
    print('<usage instructions will be here>')

def parse_posts(posts_folder, output_folder):
    # Save the Markdown instance for improved performance.
    markdown = mistune.Markdown()

    for dir_entry in os.listdir(posts_folder):
        path = os.path.join(posts_folder, dir_entry)
        filename, extension = os.path.splitext(dir_entry)
        if extension == '.markdown' and os.path.isfile(path):
            with open(path) as post:
                title = filename
                markdown_content = post.read()
                html_content = markdown(markdown_content)

                print(title)
                print(html_content)

if __name__ == '__main__':
    main(sys.argv[1:])
