from PIL import Image
from PIL.ImageOps import exif_transpose
from enum import auto, Enum
from functools import cached_property, cache
from inspect import signature
from textwrap import dedent
from os.path import basename


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

    def __init__(self, image, credit=None, caption=None):
        self.image = image
        self.caption = caption
        self.credit = credit

    def __str__(self):
        captioned = "captioned" if self.caption else ""
        caption = f'<p class="caption">{self.caption}</p>' if captioned else ""
        credit = f'<p class="credit">Photo Credit: {self.credit}</p>' if self.credit else ""

        return f"""
        <div class="zoomable {self.type} {captioned}">
            {caption}
            <div class=relative-wrapper>
                <img src={self.image} class="row-element {self.type}" onclick="toggleFullscreen(this)">
                <div class=show-on-hover>
                    <p>click to zoom</p>
                </div>
                {credit}
            </div>
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


class ImageRow(Row):

    def __init__(self, image: str | ImageWithMetadata):
        self.image, = normalize_images(image)

    def html(self):
        return dedent(f"""
            <span class="image {self.image.type} row">
                {self.image}
            </span>
            """)


class ImageImageRow(Row):

    def __init__(self, left: str | ImageWithMetadata, right: str | ImageWithMetadata):
        left, right = normalize_images(left, right)
        self.left = left
        self.right = right

    def html(self):
        return dedent(f"""
            <span class="image-image {self.left.type}-{self.right.type} row">
                {self.left}
                {self.right}
            </span>
            """)


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

    def __init__(self, heading: str, subheading: str):
        self.heading = heading
        self.subheading = subheading

    def html(self):
        return dedent(f"""
            <span class="header row">
                <h1 id="{self.heading}">{self.heading}</h1>
                <h4>{self.subheading}</h4>
            </span>
        """)


class ParagraphRow(Row):

    def __init__(self, text):
        self.text = text

    def html(self):
        return f'<span class="paragraph row"><p>{self.text}</p></span>'


class CaptionRow(Row):

    def __init__(self, caption):
        self.caption = caption

    def html(self):
        return f'<span class="row"><p class="caption">{self.caption}</p></span>'


class VideoRow(Row):

    def __init__(self, video, caption):
        self.video = video
        self.caption = caption

    def html(self):
        return dedent(f"""
            <span class="video row">
                <iframe src="https://www.youtube-nocookie.com/embed/{self.video}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                <p class="video-caption">
                {self.caption}
                </p>
            </span>
            """)


class Link():

    def __init__(self, name, prefix=""):
        self.name = name
        self.prefix = prefix
        self.title = self.name_to_title(name)

    def __str__(self):
        if self.name == "None":
            return ""
        return f"{self.prefix}<a href={self.name}.html>{self.title}</a>"

    def name_to_title(self, name):
        filename = basename(name)
        return filename.title().replace("-", " ")


class FooterRow(Row):

    def __init__(self, previous, index, next):
        self.previous = Link(previous, "Previous: ")
        self.index = Link(index)
        self.next = Link(next, "Next: ")

    def html(self):
        return dedent(f"""
            <span class="footer row">
                <p class="previous">
                {self.previous}
                </p>

                <p class="index">
                {self.index}
                </p>

                <p class="next">
                {self.next}
                </p>
            </span>
        """)