from PIL import Image
from importlib.resources import files as resource_files
from mksite.index import Index
from mksite.row import Row
from os import chdir
from os.path import abspath
from os.path import basename
from os.path import exists
from os.path import getmtime
from os.path import isdir
from os.path import isfile
from os.path import join
from os.path import split
from os.path import splitext
from oyaml import load, Loader
from re import match
from shutil import copy2
from shutil import copytree
from textwrap import dedent
from typing import Iterable


def generate_page(rows: Iterable[Row], output_path: str, modified_time: float):
    start = dedent(f"""    <!--{modified_time}-->
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="styles.css">
        <script src="scripts.js"></script>
    </head>
    <body>
    <span id=controls>
        <button id=slideshow-button onClick=slideShow()>Slides</button>
        <button id=help onClick=help()>Help</button>
        <div id=help-dialog>
          <span>
            <p>
              Click any image on the page to see it fullscreen.
            </p>
            <p>
              Use the "Slides" button to the left to enter Slides view; then
              navigate forward and backward using your arrow keys, or
              by clicking/tapping on the right and left side of the screen,
              respectively.
            </p>
            <p>
              Note: iOS <a href=https://developer.apple.com/forums/thread/133248>does
              not support fullscreen</a>, so neither of the above features will work on
              an iPhone/iPad.
            </p>
          </span>
        </div>
    </span>
    <div id=rows-container>
    """)

    end = """
    </div>
    <div id=fullscreen-container></div>
    </body>
    """

    with open(output_path, 'w') as output_file:
        output_file.write(start)
        for row in rows:
            output_file.write(row.html())
        output_file.write(end)


def parse_to_rows(input_path: str) -> Iterable[Row]:
    with open(input_path) as yaml_file:
        data = load(yaml_file.read(), Loader=Loader)
        return [Row.get_row(node) for node in data]


def safe_copytree(input_directory: str, output_directory: str, **kwargs) -> bool:
    try:
        copytree(input_directory, output_directory, **kwargs)
        return True
    except FileExistsError:
        response = input("Overwrite existing files? [y/N]")
        kwargs['dirs_exist_ok'] = True
        if response == "y":
            copytree(input_directory, output_directory, **kwargs)
            return True
        else:
            return False


def to_html_path(path: str) -> str:
    return splitext(path)[0] + ".html"


def is_yml(path: str) -> bool:
    return is_type (path, (".yml", ".yaml"))


def is_jpg(path: str) -> bool:
    return is_type (path, (".jpg", ".jpeg"))


def is_type(path: str, extensions: tuple[str, ...]) -> bool:
    return splitext(path)[1].lower() in extensions


def copy_if_newer(input_path, output_path):
    if isdir(output_path):
        output_path = join(output_path, input_path)

    output_path_exists = exists(output_path)

    if output_path_exists and not isfile(output_path):
        raise Exception(f"Refusing to copy a file over a directory: {input_path}, {output_path}")

    if output_path_exists and getmtime(output_path) >= getmtime(input_path):
        return
    else:
        copy2(input_path, output_path)


def copy_and_scale_if_newer(input_path: str, output_path: str):
    if isdir(output_path):
        input_base, ext = splitext(input_path)
        input_path_1080 = f"{input_base}.1080{ext}"
        input_path_4k = f"{input_base}.4k{ext}"
        output_path_1080 = join(output_path, input_path_1080)
        output_path_4k = join(output_path, input_path_4k)
        output_path = join(output_path, input_path)
    else:
        output_base, ext = splitext(output_path)
        output_path_1080 = f"{output_base}.1080{ext}"
        output_path_4k = f"{output_base}.4k{ext}"

    output_path_1080_exists = exists(output_path_1080)
    output_path_4k_exists = exists(output_path_4k)
    output_path_exists = exists(output_path)

    if output_path_1080_exists and not isfile(output_path_1080):
        raise Exception(f"Refusing to copy a file over a directory: {input_path}, {output_path_1080}")

    if output_path_4k_exists and not isfile(output_path_4k):
        raise Exception(f"Refusing to copy a file over a directory: {input_path}, {output_path_4k}")

    image = Image.open(input_path)

    if not output_path_1080_exists or getmtime(output_path_1080) < getmtime(input_path):
        scaled = scale_image(image, 1080)
        scaled.save(output_path_1080)
    if not output_path_4k_exists or getmtime(output_path_4k) < getmtime(input_path):
        scaled = scale_image(image, 2160)
        scaled.save(output_path_4k)
    if not output_path_exists or getmtime(output_path) < getmtime(input_path):
        copy2(input_path, output_path)


def scale_image(image: Image.Image, desired_height):
    width = int(image.width * (desired_height / image.height))
    return image.resize((width, desired_height), Image.Resampling.LANCZOS)


def generate_from_yml(input_path, output_path):
    is_index = splitext(basename(input_path))[0] == "index"
    output_dir = split(output_path)[0]
    output_path = to_html_path(output_path)
    if exists(output_path):
        with open(output_path) as existing_html:
            first_line = existing_html.readline()
            created_from = float(match("<!--(.+)-->\n", first_line).groups()[0])
            if created_from == getmtime(input_path):
                return

    if is_index:
        Index.from_file(input_path).generate_html(output_dir)
    else:
        rows = parse_to_rows(input_path)
        generate_page(rows, to_html_path(output_path), getmtime(input_path))


def generate_site(input_directory: str, output_directory: str):
    """
    Given an input directory and an output directory:

    Parse all yaml files recursively, producing symmetric html files
    copy in CSS and JS

    Copy all images files, resizing for web

    Create docker file
    """
    input_directory = abspath(input_directory)
    output_directory = abspath(output_directory)
    yml_files = []

    def copy_or_capture(input_path, output_path):
        if is_yml(input_path):
            yml_files.append((input_path, output_path))
        elif is_jpg(input_path):
            copy_and_scale_if_newer(input_path, output_path)
        else:
            copy_if_newer(input_path, output_path)

    if not safe_copytree(input_directory, output_directory, copy_function=copy_or_capture):
        exit(1)
    copytree(str(resource_files('mksite.resources').joinpath("")), output_directory, dirs_exist_ok=True)

    chdir(output_directory)
    for input_path, output_path in yml_files:
        generate_from_yml(input_path, output_path)


if __name__ == "__main__":
    from sys import argv
    generate_site(argv[1], argv[2])
