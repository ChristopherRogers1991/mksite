from src.mksite.row import Row
from os import walk, remove, chdir
from os.path import join
from oyaml import load, Loader
from shutil import copytree
from textwrap import dedent
from typing import Iterable
from importlib.resources import files as resource_files


def generate_page(rows: Iterable[Row], output_path: str):
    start = dedent("""
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
              Click any image on the page to see it fullscreen.<br/><br/>

              Use the "Slides" button to the left to enter Slides view; then
              navigate forward and backward using your arrow keys, or
              by clicking/tapping on the right and left side of the screen,
              respectively.
            </p>
          </span>
        </div>
    </span>
    """)

    end = """
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


def generate_site(input_directory: str, output_directory: str):
    """
    Given an input directory and an output directory:

    Parse all yaml files recursively, producing symmetric html files
    copy in CSS and JS

    Copy all images files, resizing for web

    Create docker file
    """
    copytree(input_directory, output_directory)
    copytree(str(resource_files('mksite.resources').joinpath("")), output_directory, dirs_exist_ok=True)
    chdir(input_directory)
    for dirpath, _, files in walk(output_directory):
        for file in files:
            if file.lower().endswith(".yml"):
                rows = parse_to_rows(join(dirpath, file))
                output_file = join(dirpath, file[:-4] + ".html")
                generate_page(rows, output_file)
                remove(join(dirpath, file))
