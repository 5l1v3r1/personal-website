import sys
import mistune
import os
import getopt
import pystache
import shutil


def main(argv):
    posts_folder, output_folder = parse_arguments(argv)
    parse_posts(posts_folder, output_folder)


def parse_arguments(argv):
    """
    Parses the command line arguments passed to the program. The allowed flags
    are:
        -h, --help: Shows the usage instructions of the program.
        -p, --posts <directory>: The directory to read posts from.
        -o, --output <directory>: The directory to output html to.

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
    print('\t-h, --help: Shows the usage instructions of the program')
    print('\t-p, --posts <directory>: The directory to read posts from.')
    print('\t-o, --output <directory>: The directory to output html to.')


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

    posts = []
    for dir_entry in os.scandir(posts_folder):
        if not dir_entry.name.startswith('.') and dir_entry.name != 'drafts': # Ignore hidden files and folders. Will not work on Windows.
            if dir_entry.is_file():
                filename, extension = os.path.splitext(dir_entry.name)
                if extension == '.markdown' or extension == '.md':
                    content = open(dir_entry.path).read()
                    html = render_post(content, filename)
                    write_file(filename + '.html', html, output_folder)
                    posts.append(filename + '.html')
                else:
                    shutil.copy(dir_entry.path, output_folder)
            elif dir_entry.is_dir():
                shutil.copytree(dir_entry.path, os.path.join(output_folder, dir_entry.name))

    html = render_index(posts)
    write_file('index.html', html, output_folder)


def read_metadata(f):
    """
    Reads a metadata block from a file object. A metadata block begins with the
    line '---' and ends with another identical line. Metadata attributes are
    divided into key and value, separated by a colon and a space. Values can
    be either single values or comma separated lists. If a value is a comma
    separated list it will be converted to a list object, otherwise it will be
    a simple string.

    :param f: A file object to read from.
    :return: A dictionary of all key-value pairs found in a metadata block in
             the given file.
    """
    metadata = dict()

    if f.readline() == '---\n':
        for line in f:
            if line == '---\n':
                break

            key, value = line.split(': ')
            value = value.rstrip() # Remove newline character \n.
            values = value.split(', ')
            if len(values) > 1:
                metadata[key] = values
            else:
                metadata[key] = value
    else:
        f.seek(0)

    return metadata


def render_post(content, title):
    """
    Renders a post to HTML and returns the result. This function is resposible
    for extracting all necessary information from the content.

    :param content: The content to render.
    :param title: The title of the post. TO BE DEPRECATED. Should be replaced
                     with YAML front matter.
    """
    content = mistune.markdown(content)

    renderer = pystache.Renderer(search_dirs='templates')
    body = renderer.render_name('blog_post', {'content': content})
    html = renderer.render_name('main', {'body': body, 'title': title})
    return html


def render_index(posts):
    renderer = pystache.Renderer(search_dirs='templates')
    body = renderer.render_name('index', {'posts': posts})
    html = renderer.render_name('main', {'body': body, 'title': 'Index'})
    return html


def write_file(filename, content, folder):
    """
    Writes a file to a folder.

    :param filename: The filename of the new file.
    :param content: The content of the new file.
    :param folder: The folder to write the new file to.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    open(path, 'w').write(content)


if __name__ == '__main__':
    main(sys.argv[1:])
