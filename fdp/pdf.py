"""
Module that provides classes useful to work with PDF objects.

"""
import json
from base64 import b64decode, b64encode
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from wand.image import Image


class JSONPDFEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PDF):
            return o.to_JSON()
        return json.JSONEncoder.default(self, o)


class File(object):
    """Basic File object that can be either an Image or a Pdf."""

    name = None
    path = None
    data = None
    thumbnail = None


class PDF(File, PdfFileReader):
    """Represents a PDF."""

    num_pages = None
    pages = []
    thumbnails = {}

    def __init__(self, data, thumbnail=None):
        """
        Creates a representation of a PDF

        :bytes data: self explanatory

        """
        self.thumbnail = thumbnail
        self.reader = PdfFileReader(BytesIO(data))
        self.num_pages = self.reader.getNumPages()
        self.title = self.reader.getDocumentInfo().title
        self.pages = dict(
            (i, x) for i, x in enumerate(self.reader.pages, start=1))
        self.generate_thumbs()

    def generate_thumbs(self, resolution=72):
        """
        Returns a thumbnail of a page
        """
        if self.thumbnail:
            self.thumbnails[1] = b64encode(self.thumbnail).decode('utf-8')
        for i, page in self.pages.items():
            writer = PdfFileWriter()
            writer.addPage(page)
            pdf_bytes = BytesIO()
            writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            with Image(file=pdf_bytes, resolution=300) as fd:
                with fd.convert("png") as thumbfd:
                    thumbfd.transform(resize='200x')
                    self.thumbnails[i] = b64encode(
                        thumbfd.make_blob()).decode('utf-8')

    def to_JSON(self):
        return {
            'num_pages': self.num_pages,
            'thumbnails': self.thumbnails,
            'title': self.title,
        }


class Picture(File):
    """
    Represents uploaded images.

    :name: name of the file
    :format: format of the file eg: jpeg, png
    """

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
        return PDF(self.data, thumbnail=self.thumbnail)
