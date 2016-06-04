import sys
import mistune
import getopt
import pystache
import shutil
import git
import datetime
import pathlib
import re
import docopt
import datetime
import dateparser


def main(argv):
    docopt_str = """
Usage:
    build_blog.py -p <folder> | --posts <folder> -o <folder> | --out <folder>
    build_blog.py -h | --help

Options:
    -h --help                      Show this screen.
    -p <folder>, --posts <folder>  Specify posts folder.
    -o <folder>, --out <folder>    Specify output folder.
"""
    opt = docopt.docopt(docopt_str, argv=argv)

    posts_folder = opt['--posts']
    output_folder = opt['--out']

    posts_path = pathlib.Path(posts_folder)
    output_path = pathlib.Path(output_folder)
    build_blog(posts_path, output_path)

    render_template('index', {'title': 'Home', 'index': True}, output_path / 'index.html')


def build_blog(posts_path, output_path):
    """
    Goes through the posts folder, parses all posts and copies the rendered
    html to the output folder. Posts must have the file ending .markdown.

    :param posts_path: The folder to read posts from. If this folder doesn't
                         exist the script will exit without doing anything.
    :param output_path: The folder to output html to. Will be created if it
                          doesn't exist.
    """
    if not posts_path.exists():
        print('Error: Folder {} does not exist.'.format(str(posts_path)))
        sys.exit(2)

    # Find all markdown files.
    files = list(posts_path.glob('**/*.markdown'))
    ignore = list(posts_path.glob('**/_*.markdown')) + list(posts_path.glob('**/_*/*.markdown')) # Ignore all files and folders that start with an underscore.

    # Parse the content of each file.
    posts = [parse_post(file, posts_path) for file in files if not file in ignore]

    # Sort by date (we assume that date exists).
    posts.sort(key=lambda post: post['date'], reverse=True)

    # Render all posts.
    for i, post in enumerate(posts):
        data = {
            'title': post['title'],
            'blog': True,
            'post': post,
            'base_url': '/blog/'
        }

        # Add links to next and previous posts.
        if not i == 0:
            data['next'] = posts[i - 1]
        if not i == len(posts) - 1:
            data['prev'] = posts[i + 1]

        render_template('blog_post', data, output_path / 'blog' / 'posts' / post['url'] / 'index.html')

    render_template('blog_index', {
        'blog': True,
        'title': 'Blog',
        'posts': posts
    }, output_path / 'blog' / 'index.html')

    all_tags = {}
    for post in posts:
        try:
            tags = post['tags']
            for tag in tags:
                if tag not in all_tags:
                    all_tags[tag] = []
                all_tags[tag].append(post)
        except KeyError:
            # Post has no tags.
            pass

    # Render all tag indices.
    for (tag, posts) in all_tags.items():
        render_template('blog_index', {
            'blog': True,
            'title': tag,
            'posts': posts
        }, output_path / 'blog' / 'tags' / tag / 'index.html')


def parse_post(path_to_file, root_path):
    """
    Parses a post written in markdown with optional metadata from a file.

    :param dir_entry: A directory entry for the post file to parse.
    :returns: A dictionary representing a single post.
    """
    # Read entire file.
    file_content = path_to_file.read_text()

    # Parse metadata.
    segments = file_content.split('\n\n')
    metadata = dict()
    if not segments[0].startswith('# '):
        # File didn't start with title => there is metadata.
        metadata = parse_metadata(segments[0])
        segments = segments[1:]

    # Split content into parts.
    title = segments[0].replace('# ', '')
    content = '\n\n'.join(segments[1:])
    first_paragraph = segments[1]

    # Generate additional attributes.
    url = path_to_file.with_suffix('').name.lower().replace(' ', '_')
    formatted_date = metadata['date'].strftime('%B %-d, %Y')
    reading_time = calculate_reading_time(content)
    commits = get_commit_history(path_to_file, root_path)
    try:
        has_tags = len(metadata['tags']) > 0
    except KeyError:
        has_tags = False
        pass

    # Transform content to HTML.
    markdown = mistune.Markdown()
    content = markdown(content)
    content = add_anchors_to_headings(content)
    first_paragraph = markdown(first_paragraph)

    # Put everything together.
    post = metadata.copy()
    post.update({
        'title': title,
        'content': content,
        'first_paragraph': first_paragraph,
        'url': url,
        'formatted_date': formatted_date,
        'reading_time': reading_time,
        'commits': commits,
        'has_tags': has_tags
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
            if key == 'date':
                metadata[key] = dateparser.parse(value)
            else:
                metadata[key] = value

    return metadata


def add_anchors_to_headings(content):
    regex = re.compile('<h(.)>(.*)<\/h\\1>') # This regex matches all headings and captures their level and their text.
    for match in re.finditer(regex, content):
        h_number = match.group(1)
        heading = match.group(2)
        anchor = '{0}'.format(heading.lower().replace(' ', '_'))

        formatted_heading = '<h{0}><a name="{1}" href="#{1}">{2}</a></h{0}>'.format(h_number, anchor, heading)

        content = content.replace(match.group(0), formatted_heading)

    return content


def calculate_reading_time(text):
    # https://medium.com/the-story/read-time-and-you-bc2048ab620c
    WPM = 275 # How many words that are read per minute.
    word_count = len(re.findall(r'\w+', text))
    return round(word_count / WPM);


def get_commit_history(path_to_file, repo_root_path):
    commits = []

    try:
        repo = git.Repo(str(repo_root_path))
        commits = [{
            'author': commit.author,
            'timestamp': datetime.datetime.fromtimestamp(commit.authored_date),
            'message': commit.message
        } for commit in repo.iter_commits(paths=path_to_file.name)]
    except StopIteration:
        pass

    return commits


def render_template(template, data, path):
    """
    Renders a template with data and writes the result to a new file.

    :param template: The name of the template to use when rendering.
    :param data: The data to use when rendering.
    :param path: The path to write the rendered file to.
    """
    path = pathlib.Path(path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    renderer = pystache.Renderer(search_dirs='templates')
    body = renderer.render_name(template, data)
    html = renderer.render_name('main', {'body': body, 'data': data})
    path.write_text(html)


if __name__ == '__main__':
    main(sys.argv[1:])
