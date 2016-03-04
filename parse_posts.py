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
    if not os.path.exists(posts_folder):
        print('Error: Folder {} does not exist'.format(posts_folder))
        sys.exit(2)

    for filename in os.listdir(posts_folder):
        path = os.path.join(posts_folder, filename)
        if is_markdown_file(path):
            title, content = parse_post_file(path)
            write_html_file(title, content, output_folder)

def is_markdown_file(path):
    extension = os.path.splitext(path)[1]
    return extension == '.markdown' and os.path.isfile(path)

def parse_post_file(path):
    filename = os.path.split(path)[1]
    title = os.path.splitext(filename)[0] # Removes extension from filename
    content = open(path).read()
    return (title, content)

def write_html_file(title, content, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = title + '.html'
    html = mistune.markdown(content)

    path = os.path.join(folder, filename)
    open(path, 'w').write(html)

if __name__ == '__main__':
    main(sys.argv[1:])
