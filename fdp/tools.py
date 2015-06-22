"""
Various useful helpers.

"""

from io import BytesIO
from wand.image import Image


def pdf2png(pdf, size):
    """Transform a PDF to a PNG thumbnail."""
    tmpjpg = BytesIO()
    io = BytesIO()
    with Image(file=pdf, resolution=300) as img:
        img.compression_quality = 100
        img.format = 'jpeg'
        img.save(file=tmpjpg)
    tmpjpg.flush()
    tmpjpg.seek(0)
    with Image(file=tmpjpg, resolution=300) as img:
        if img.width > 400:
            img.transform(resize='%sx' % size)
        img.save(file=io)
    io.flush()
    io.seek(0)
    return io
