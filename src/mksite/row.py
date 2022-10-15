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

    def __init__(self, image, caption=None):
        self.image = image
        self.caption = caption

    def __str__(self):
        captioned = "captioned" if self.caption else ""
        caption = f'<p class="caption">{self.caption}</p>' if captioned else ""

        return f"""
        <div class=zoomable>
            <span>
                <img src={self.image} class="row-element {self.type} {captioned}" onclick="fullScreenImage(this)"/>
                <p class=show-on-hover>click to zoom</p>
                {caption}
            </span>
        </div>
        """

    @cached_property
    def type(self):
        return ImageType.get_image_type(self.image)


def normalize_images(*args):
    results = []
    for arg in args:
        results.append(ImageWithMetadata(**arg) if type(arg) is dict else ImageWithMetadata(arg))
    return tuple(results)


@cache
def get_init_args(cls):
    return list(signature(cls.__init__).parameters.keys())[1:]


class Row():

    @property
    def accepted_image_types(self):
        return ()

    def html(self):
        raise Exception("Must be implemented by subclasses")

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
        left, right = normalize_images(left, right)
        self.left = left
        self.right = right

    def html(self):
        return dedent(f"""
            <span class="image-image row">
                {self.left}
                {self.right}
            </span>
            """)


# TODO - can type normalization be done with a decorator?
class ImageImageImageRow(Row):
    def __init__(self,
                 left: str | ImageWithMetadata,
                 center: str | ImageWithMetadata,
                 right: str | ImageWithMetadata):
        left, center, right = normalize_images(left, center, right)
        self.validate_image_types(left, center, right)
        self.left = left
        self.center = center
        self.right = right

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL,

    def html(self):
        return dedent(f"""
            <span class="image-image-image row">
                {self.left}
                {self.center}
                {self.right}
            </span>
            """)


class TextImageRow(Row):

    def __init__(self, text: str, image: str | ImageWithMetadata):
        image, = normalize_images(image)
        self.validate_image_types(image)
        self.text = text
        self.image = image

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL, ImageType.HORIZONTAL

    def html(self):
        return dedent(f"""
            <span class="text-image row">
                <p class=side-text>
                    {self.text}
                </p>
                {self.image}
            </span>
            """)


class ImageTextRow(Row):

    def __init__(self, image: str | ImageWithMetadata, text: str):
        image, = normalize_images(image)
        self.validate_image_types(image)
        self.text = text
        self.image = image

    @property
    def accepted_image_types(self):
        return ImageType.VERTICAL, ImageType.HORIZONTAL

    def html(self):
        return dedent(f"""
            <span class="image-text row">
                {self.image}
                <p class=side-text>
                    {self.text}
                </p>
            </span>
            """)


class HeaderRow(Row):

    def __int__(self, heading, subheading):
        self.heading = heading
        self.subheading = subheading

    def html(self):
        return dedent(f"""
            <h1 id="{self.heading}" class="row">{self.heading}</h1>
            <h4 class="row">{self.subheading}</h4>
        """)


class ParagraphRow(Row):

    def __init__(self, text):
        self.text = text

    def html(self):
        return f'<span class="row"><p>{self.text}</p></span>'


class CaptionRow(Row):

    def __init__(self, caption):
        self.caption = caption

    def html(self):
        return f'<span class="row"><p class="caption">{self.caption}</p></span>'


class VideoRow(Row):

    def __int__(self, id, caption):
        self.id = id
        self.caption = caption

    def html(self):
        return dedent(f"""
            <span class="video-text row">
                <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/{self.id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </span>
            <span class="row">
                <p class="caption">
                {self.caption}
                </p>
            </span>
            """)
