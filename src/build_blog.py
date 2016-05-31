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
    All non-post files will be copied to the output folder without modification.

    :param posts_path: The folder to read posts from. If this folder doesn't
                         exist the script will exit without doing anything.
    :param output_path: The folder to output html to. Will be created if it
                          doesn't exist.
    """
    if not posts_path.exists():
        print('Error: Folder {} does not exist.'.format(str(posts_path)))
        sys.exit(2)

    files = list(posts_path.glob('**/*.markdown'))
    # Ignore all files and folders that start with an underscore.
    ignore = list(posts_path.glob('**/_*.markdown')) + list(posts_path.glob('**/_*/*.markdown'))

    posts = [parse_post(file, posts_path) for file in files if not file in ignore]
    posts.sort(key=lambda post: post['date'], reverse=True)

    all_tags = {}

    for i, post in enumerate(posts):
        post['date'] = post['date'].strftime('%B %-d, %Y')

        data = {
            'title': post['title'],
            'post': post,
            'blog': True
        }

        if not i == 0:
            data['next'] = posts[i - 1]
        if not i == len(posts) - 1:
            data['prev'] = posts[i + 1]

        render_template('blog_post', data, output_path / 'blog' / 'posts' / post['url'] / 'index.html')

        try:
            post['has-tags'] = True
            tags = data['post']['tags']
            for tag in tags:
                if tag not in all_tags:
                    all_tags[tag] = []
                all_tags[tag].append(post)
        except KeyError:
            # Post has no tags.
            post['has-tags'] = False
            pass

    render_template('blog_index', {
        'blog': True,
        'title': 'Blog',
        'posts': posts
    }, output_path / 'blog' / 'index.html')

    for (tag, posts) in all_tags.items():
        render_template('blog_index', {
            'blog': True,
            'title': tag,
            'posts': posts
        }, output_path / 'blog' / 'tags' / tag / 'index.html')


def parse_post(full_path, root_path):
    """
    Parses a post written in markdown with optional metadata from a file.

    :param dir_entry: A directory entry for the post file to parse.
    :returns: A dictionary representing a single post.
    """
    file_content = full_path.read_text()
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

    reading_time = calculate_reading_time(file_content)

    # This regex matches all headings and captures their level and their text.
    regex = re.compile('<h(.)>(.*)<\/h\\1>')
    for match in re.finditer(regex, content):
        h_number = match.group(1)
        heading = match.group(2)
        anchor = '{0}'.format(heading.lower().replace(' ', '_'))

        formatted_heading = '<h{0}><a name="{1}" href="#{1}">{2}</a></h{0}>'.format(h_number, anchor, heading)

        content = content.replace(match.group(0), formatted_heading)

    # A simpler way to add links to headings. Though with this method you can't
    # change the string captured by group 2 from what I can tell.
    # content = regex.sub('<h\\1><a href="#\\2">\\2</a></h\\1>', content)

    try:
        repo = git.Repo(str(root_path))
        commits = [{
            'author': commit.author,
            'timestamp': datetime.datetime.fromtimestamp(commit.authored_date),
            'message': commit.message
        } for commit in repo.iter_commits(paths=full_path.name)]
    except StopIteration:
        pass

    url = full_path.with_suffix('').name.lower().replace(' ', '_')

    post = metadata.copy()
    post.update({
        'title': title,
        'first_paragraph': first_paragraph,
        'content': content,
        'url': url,
        'commits': commits,
        'date': dateparser.parse(post['date']),
        'reading_time': reading_time
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


def calculate_reading_time(text):
    WPM = 275
    word_count = len(re.findall(r'\w+', text))
    return round(word_count / WPM);


if __name__ == '__main__':
    main(sys.argv[1:])
