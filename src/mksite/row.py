from PIL import Image
from PIL.ImageOps import exif_transpose
from enum import auto, Enum
from functools import cached_property, cache
from inspect import signature
from textwrap import dedent


class ImageType(Enum):
    HORIZONTAL = auto()
    HORIZONTAL_WIDE = auto()
    VERTICAL = auto()

    @classmethod
    def get_image_type(cls, file_path: str):
        image = Image.open(file_path)
        image = exif_transpose(image)
        ratio = image.width / image.height
        if ratio > 2:
            return cls.HORIZONTAL_WIDE
        if ratio > 1:
            return cls.HORIZONTAL
        return cls.VERTICAL

    def __str__(self):
        return self.name


class ImageWithMetadata():

    def __init__(self, file_path, caption=None):
        self.file_path = file_path
        self.caption = caption

    def __str__(self):
        return f'''
        <div class=zoomable>
            <img src={self.file_path} class="row-element {self.type}" onclick="fullScreenImage(this)"/>
            <p class=show-on-hover>click to zoom</p>
        </div>
        '''

    @cached_property
    def type(self):
        return ImageType.get_image_type(self.file_path)

@cache
def get_init_args(cls):
    return list(signature(cls.__init__).parameters.keys())[1:]


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
            <span class="image-image row">
                {left}
                {right}
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
            <span class="image-image-image row">
                {left}
                {center}
                {right}
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
            <span class="text-image row">
                <p>
                    {text}
                </p>
                {image}
            </span>
            """)


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
            <span class="text-image row">
                {image}
                <p>
                    {text}
                </p>
            </span>
            """)
