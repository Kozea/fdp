import json
from . import url, Route
from .pdf import Picture, PDF, JSONPDFEncoder
from copy import copy
from io import BytesIO
from base64 import b64encode
from PyPDF2 import PdfFileReader, PdfFileWriter


@url(r'/')
class Merge(Route):
    def get(self):
        return self.render('index.html')

    def post(self):
        json_data = json.loads(self.request.body.decode('utf-8'))
        order = json_data.get('order', None)
        pdfs = json_data.get('pdfs_list', None)
        writer = PdfFileWriter()
        loaded_pdfs = {}
        for pdf in pdfs:
            reader = PdfFileReader(pdf)
            loaded_pdfs[pdf] = reader
        for i, page in sorted(order.items()):
            # we need a shallow copy here else we get a ref to
            # the same object if there is a copy of the page
            source = copy(loaded_pdfs.get(page.get('pdf')))
            page_number = page.get('id') - 1
            rotation = page.get('rotation', 0)
            pdf_page = source.getPage(page_number)
            method = ('rotateClockwise' if rotation > 0 else
                      'rotateCounterClockwise')
            getattr(pdf_page, method)(abs(rotation))
            writer.addPage(pdf_page)
        _file = BytesIO()
        writer.write(_file)
        _file.seek(0)
        self.set_header('Content-Type', 'application/pdf')
        self.set_header('Content-Disposition',
                        'attachment; filename=pdf.pdf')
        self.write(b64encode(_file.read()))


@url('/upload')
class Upload(Route):
    def post(self):
        files = []
        for fn in self.request.files['file']:
            if fn.content_type != 'application/pdf':
                img = Picture()
                img.populate_from_stream(fn)
                obj = img.toPDF()
            else:
                obj = PDF(fn.body)
            files.append(obj)
        return self.write(JSONPDFEncoder().encode(files))
