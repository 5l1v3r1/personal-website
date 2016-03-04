import sys
import mistune
import os
import getopt


def main(argv):
    posts_folder, output_folder = parse_arguments(argv)
    parse_posts(posts_folder, output_folder)


def parse_arguments(argv):
    """
    Parses the command line arguments passed to the program. The allowed flags
    are:
        -h, --help: Shows the usage instructions of the program.
        -p, --posts: The directory to read posts from.
        -o, --output: The directory to output html to.

    If the arguments don't match the specification the usage instructions
    for the program is shown.

    :param argv: A list of command line arguments.
    :return: A folder to read posts from and a folder to output html to.
    """
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

    return posts, output


def invalid_arguments():
    """
    Prints the usage instructions for the program and exits with error code 2.
    """
    print_usage_instructions()
    sys.exit(2)  # Exit code 2 = command line syntax error


def print_usage_instructions():
    """
    Prints the usage instructions for the program.
    """
    print('parse_posts.py usage:\n')
    print('\t-h, --help:\tShows the usage instructions of the program')
    print('\t-p, --posts:\tThe directory to read posts from.')
    print('\t-o, --output:\tThe directory to output html to.')


def parse_posts(posts_folder, output_folder):
    """
    Parses all posts in the posts folder, parses their content and outputs
    generated html to the output folder. The posts have to have the file ending
    .markdown or .md.

    :param posts_folder: The folder to read posts from.
    :param output_folder: The folder to output html to.
    """
    if not os.path.exists(posts_folder):
        print('Error: Folder {} does not exist'.format(posts_folder))
        sys.exit(2)

    markdown = mistune.Markdown()  # Save the Markdown instance for improved performance.

    for path in filter(is_markdown_file, [os.path.join(posts_folder, x) for x in os.listdir(posts_folder)]):
        title, content = parse_post_file(path)
        html = markdown(content)
        write_html_file(title, html, output_folder)


def is_markdown_file(path):
    """
    Checks whether or not an item in a directory listing is a markdown file.
    Markdown files have the file ending .markdown or .md.

    :param path: The path to the file or folder to check.
    """
    extension = os.path.splitext(path)[1]
    return (extension == '.markdown' or extension == '.md') and os.path.isfile(path)


def parse_post_file(path):
    """
    Parses a post file and returns a touple with the title and the content of
    the post. The title will be the filename without the file ending.

    :param path: The post file to parse. This has to be a valid file.
    :return: (title, content) where title is the filename of the file without
             its file ending, and content is the body of the file.
    """
    filename = os.path.split(path)[1]
    title = os.path.splitext(filename)[0]  # Removes extension from filename
    content = open(path).read()
    return title, content


def write_html_file(filename, content, folder):
    """
    Writes an html file to the specified folder. The full filename of this file
    will be filename + '.html'.

    :param filename: The filename of the new file (without file ending)
    :param content: The content to write to the file.
    :param folder: The folder to write the new file to.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = filename + '.html'
    path = os.path.join(folder, filename)
    open(path, 'w').write(content)


if __name__ == '__main__':
    main(sys.argv[1:])
