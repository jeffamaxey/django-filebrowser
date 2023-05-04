# coding: utf-8

import math
import os
import re
import unicodedata

import six

from django.utils.module_loading import import_string
from filebrowser.settings import (CONVERT_FILENAME, NORMALIZE_FILENAME,
                                  STRICT_PIL, VERSION_PROCESSORS)

if STRICT_PIL:
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        import Image


def convert_filename(value):
    """
    Convert Filename.
    """

    if NORMALIZE_FILENAME:
        chunks = value.split(os.extsep)
        normalized = []
        for v in chunks:
            v = unicodedata.normalize('NFKD', six.text_type(v)).encode('ascii', 'ignore').decode('ascii')
            v = re.sub(r'[^\w\s-]', '', v).strip()
            normalized.append(v)

        value = '.'.join(normalized) if len(normalized) > 1 else normalized[0]
    if CONVERT_FILENAME:
        value = value.replace(" ", "_").lower()

    return value


def path_strip(path, root):
    if not path or not root:
        return path
    path = os.path.normcase(path)
    root = os.path.normcase(root)
    return path[len(root):] if path.startswith(root) else path


_default_processors = None


def process_image(source, processor_options, processors=None):
    """
    Process a source PIL image through a series of image processors, returning
    the (potentially) altered image.
    """
    global _default_processors
    if processors is None:
        if _default_processors is None:
            _default_processors = [import_string(name) for name in VERSION_PROCESSORS]
        processors = _default_processors
    image = source
    for processor in processors:
        image = processor(image, **processor_options)
    return image


def scale_and_crop(im, width=None, height=None, opts='', **kwargs):
    """
    Scale and Crop.
    """
    x, y = [float(v) for v in im.size]
    width = float(width or 0)
    height = float(height or 0)

    if (x, y) == (width, height):
        return im

    if (
        'upscale' not in opts
        and (x < width or not width)
        and (y < height or not height)
    ):
        return im

    xr = width if width else float(x * height / y)
    yr = height if height else float(y * width / x)
    r = max(xr / x, yr / y) if 'crop' in opts else min(xr / x, yr / y)
    if r < 1.0 or (r > 1.0 and 'upscale' in opts):
        im = im.resize((int(math.ceil(x * r)), int(math.ceil(y * r))), resample=Image.ANTIALIAS)

    if 'crop' in opts:
        x, y = [float(v) for v in im.size]
        ex, ey = (x - min(x, xr)) / 2, (y - min(y, yr)) / 2
        if ex or ey:
            im = im.crop((int(ex), int(ey), int(ex + xr), int(ey + yr)))
    return im

scale_and_crop.valid_options = ('crop', 'upscale')


def get_modified_time(storage, path):
    if hasattr(storage, "get_modified_time"):
        return storage.get_modified_time(path)
    return storage.modified_time(path)
