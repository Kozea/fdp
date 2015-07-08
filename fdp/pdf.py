"""
Module that provides classes useful to work with PDF objects.

"""

from PyPDF2 import PdfFileReader
from io import BytesIO
from wand.image import Image


class File(object):
    """Basic File object that can be either an Image or a Pdf."""

    name = None
    path = None
    data = None


class PDF(File, PdfFileReader):
    """Represents a PDF."""

    pages = None
    thumbnails = {}

    def __init__(self, data):
        """
        Creates a representation of a PDF

        :bytes data: self explanatory

        """
        self.reader = PdfFileReader(BytesIO(data))
        self.pages = self.reader.getNumPages()


class Picture(File):
    """
    Represents uploaded images.

    :name: name of the file
    :format: format of the file eg: jpeg, png
    """

    def __init__(self):
        pass

    def populate_from_stream(self, httpfile, name=None):
        """
        Populates the fields of the object using a stream ie upload.

        :httpfile: request.files from tornado
        :name: optional name to give to this file

        """

        self.raw_data = httpfile.body
        self.thumbnail = b''
        self.name = name or httpfile.filename
        self.type = httpfile.content_type

        with Image(file=BytesIO(self.raw_data), resolution=300) as fd:
            with fd.convert(fd.format) as thumbfd:
                thumbfd.transform(resize='200x')
                self.thumbnail = thumbfd.make_blob()
            fd.format = 'pdf'
            self.data = fd.make_blob()

    def toPDF(self):
        return PDF(self.data)
