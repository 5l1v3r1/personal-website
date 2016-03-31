import sys
import mistune
import os
import getopt
import pystache
import shutil
import git
import datetime
import pathlib


def main(argv):
    posts_folder, output_folder = parse_arguments(argv)
    build_blog(posts_folder, output_folder)


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


def build_blog(posts_folder, output_folder):
    """
    Goes through the posts folder, parses all posts and copies the rendered
    html to the output folder. Posts must have the file ending .markdown
    or .md. All non-post files will be copied to the output folder without
    modification.

    :param posts_folder: The folder to read posts from. If this folder doesn't
                         exist the script will exit without doing anything.
    :param output_folder: The folder to output html to. Will be created if it
                          doesn't exist.
    """
    if not os.path.exists(posts_folder):
        print('Error: Folder {} does not exist'.format(posts_folder))
        sys.exit(2)

    posts_path = pathlib.Path(posts_folder)
    markdown_files = posts_path.glob('**/*.markdown')

    posts = [parse_post(post_file) for post_file in markdown_files]
    posts.sort(key=lambda post: post['date'], reverse=True)

    for i, post in enumerate(posts):
        data = {
            'title': post['title'],
            'post': post
        }

        if not i == 0:
            data['next'] = posts[i - 1]
        if not i == len(posts) - 1:
            data['prev'] = posts[i + 1]

        render_template('blog_post', data, os.path.join(output_folder, post['url']))

    render_template('blog_index', {'title': 'blog', 'posts': posts}, os.path.join(output_folder, 'blog.html'))


def parse_post(path):
    """
    Parses a post written in markdown with optional metadata from a file.

    :param dir_entry: A directory entry for the post file to parse.
    :returns: A dictionary representing a single post.
    """
    file_content = path.open().read()
    segments = file_content.split('\n\n')

    metadata = dict()
    if not segments[0].startswith('# '):
        # File didn't start with title -> there is metadata.
        metadata = parse_metadata(segments[0])
        segments = segments[1:]

    markdown = mistune.Markdown()

    title = segments[0].replace('# ', '')
    first_paragraph = markdown(segments[1])
    content = markdown('\n\n'.join(segments[2:]))

    repo = git.Repo(path.parts[0])
    latest_commit = next(repo.iter_commits(paths=path.name))
    date = datetime.date.fromtimestamp(latest_commit.authored_date)

    post = metadata.copy()
    post.update({
        'date': date,
        'title': title,
        'first_paragraph': first_paragraph,
        'content': content,
        'url': str(path.with_suffix('.html'))
    })

    return post


def parse_metadata(block):
    """
    Parses a block of metadata. Metadata attributes are divided into key and
    value, separated by a colon and a space, with one attribute per line. Values
    can be either single values or comma separated lists. If a value is a comma
    separated list it will be converted to a list object, otherwise it will be
    a simple string.

    :param block: A string with a block of metadata.
    :return: A dictionary of all key-value pairs found in a metadata block.
    """
    metadata = dict()
    lines = block.split('\n')
    for line in lines:
        key, value = line.split(': ')
        values = value.split(', ')
        if len(values) > 1:
            metadata[key] = values
        else:
            metadata[key] = value

    return metadata


def render_template(template, data, path):
    """
    Renders a template and writes it to a new html file.

    :param template: The name of the template to use when rendering.
    :param data: The data to use when rendering.
    :param output_folder: The folder to write the new html file to.
    """
    path = pathlib.Path(path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    renderer = pystache.Renderer(search_dirs='templates')
    body = renderer.render_name(template, data)
    html = renderer.render_name('main', {'body': body, 'title': data['title']})
    open(str(path), 'w').write(html)


if __name__ == '__main__':
    main(sys.argv[1:])
