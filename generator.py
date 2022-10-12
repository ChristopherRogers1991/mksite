from enum import Enum, auto

from oyaml import load, Loader
from PIL import Image
from inspect import signature
from functools import cache, cached_property
from typing import Iterable
from os import walk, mkdir
from os.path import join, exists, isdir
from shutil import copy, copytree
from textwrap import dedent


class ImageType(Enum):
    HORIZONTAL = auto()
    HORIZONTAL_WIDE = auto()
    VERTICAL = auto()

    @classmethod
    def get_image_type(cls, file_path: str):
        image = Image.open(file_path)
        ratio = image.height / image.width
        if ratio > 2:
            return cls.HORIZONTAL_WIDE
        if ratio > 1:
            return cls.HORIZONTAL
        return cls.VERTICAL


class ImageWithMetadata():

    def __init__(self, file_path, caption=None):
        self.file_path = file_path
        self.caption = caption

    def __str__(self):
        return self.file_path

    @cached_property
    def type(self):
        return ImageType.get_image_type(self.file_path)


class Row():

    @property
    def base_html(self):
        raise Exception("Must be implemented by subclasses")

    @property
    def accepted_image_types(self):
        return ()

    def html(self):
        return self.base_html.format(**self.__dict__)

    def validate_image_types(self, *images):
        for image in images:
            image_type = image.type if type(image) == ImageWithMetadata else ImageType.get_image_type(image)
            if image_type not in self.accepted_image_types:
                raise Exception(f"{self.__class__.__name__} only supports {self.accepted_image_types}. "
                                f"Type was {image_type}")

    @classmethod
    def get_row(cls, kwargs):
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            args = get_init_args(subclass)
            if args == list(kwargs.keys()):
                return subclass(**kwargs)
        raise Exception(f"Arguments did not match any type. {kwargs}")


class ImageImageRow(Row):

    def __init__(self, left: str | ImageWithMetadata, right: str | ImageWithMetadata):
        if type(left) == str:
            left = ImageWithMetadata(left)
        if type(right) == str:
            right = ImageWithMetadata(right)
        self.left = left
        self.right = right

    @cached_property
    def base_html(self):
        return dedent("""
                <img src={left} class="row-element"/>
                <img src={right} class="row-element"/>
            </span>
            """)


# TODO - can type normalization be done with a decorator?
class ImageImageImageRow(Row):
    def __init__(self,
                left: str | ImageWithMetadata,
                center: str | ImageWithMetadata,
                right: str | ImageWithMetadata):
        if type(left) == str:
            left = ImageWithMetadata(left)
        if type(center) == str:
            center = ImageWithMetadata(center)
        if type(right) == str:
            right = ImageWithMetadata(right)
        self.validate_image_types(left, center, right)
        self.left = left
        self.center = center
        self.right = right

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL,

    @cached_property
    def base_html(self):
        return dedent("""
            <span>
                <img src={left} class="row-element"/>
                <img src={center} class="row-element"/>
                <img src={right} class="row-element"/>
            </span>
            """)


class TextImageRow(Row):

    def __init__(self, text: str, image: str | ImageWithMetadata):
        if type(image) == str:
            image = ImageWithMetadata(image)
        self.validate_image_types(image)
        self.text = text
        self.image = image

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL, ImageType.HORIZONTAL

    @property
    def base_html(self):
        return dedent("""
            <span class="text-image row {image_type}">
                <p>
                    {text}
                </p>
                <img src={file_path} class="row-element"/>
            </span>
            """)

    def html(self):
        return self.base_html.format(image_type = self.image.type,
                                     text = self.text,
                                     file_path = self.image.file_path)


class ImageTextRow(Row):

    def __init__(self, image: str | ImageWithMetadata, text: str):
        if type(image) == str:
            image = ImageWithMetadata(image)
        self.validate_image_types(image)
        self.text = text
        self.image = image

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL, ImageType.HORIZONTAL

    @cached_property
    def base_html(self):
        return dedent("""
            <span class="text-image row {image_type}">
                <img src={file_path} class="row-element"/>
                <p>
                    {text}
                </p>
            </span>
            """)

    def html(self):
        return self.base_html.format(image_type = self.image.type,
                                     text = self.text,
                                     file_path = self.image.file_path)


@cache
def get_init_args(cls):
    return list(signature(cls.__init__).parameters.keys())[1:]


def generate_page(rows: Iterable[Row], output_path: str):
    start = dedent("""
    <head>
        <link rel="stylesheet" href="styles.css">
        <script src="scripts.js"></script>
    </head>

    <body>
    """)

    end = "</body>"

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
    # try:
    #     mkdir(output_directory)
    # except
    # for dirpath, _, files in walk(input_directory):
    #     current_output = join(output_directory, dirpath)
    #     mkdir(join(current_output))
    #     for file in files:
    #         if not file.lower().endswith(".yml"):
    #             copy(join(dirpath, file), current_output)
    #         else:
    #             output_file = join(dirpath, file[:-4] + ".html")
    #             rows = parse_to_rows(join(dirpath, file))
    #             generate_page(rows, output_file)

    copytree(input_directory, output_directory)
    for dirpath, _, files in walk(output_directory):
        for file in files:
            if file.lower().endswith(".yml"):
                rows = parse_to_rows(join(dirpath, file))
                output_file = join(dirpath, file[:-4] + ".html")
                generate_page(rows, output_file)
