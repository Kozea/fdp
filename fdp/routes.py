from . import url, Route
from .tools import pdf2png
from io import BytesIO
from base64 import b64encode
from PyPDF2 import PdfFileReader, PdfFileWriter
from wand.image import Image
from tornado.escape import json_encode


@url(r'/')
class Merge(Route):
    def get(self):
        return self.render('index.html')

    def post(self):
        pdfs = self.request.files.get('files[]', None)
        pages = int(len(self.request.arguments) / 3)
        output = PdfFileWriter()
        bodies = {}
        if not pdfs:
            return
        for el in pdfs:
            if el.filename not in bodies:
                bodies[el.filename] = el.body
                # if the body is an image we must convert it to pdf first
                if el.content_type != 'application/pdf':
                    bodies[el.filename] = image2Pdf(el.body).read()
        if pdfs:
            filename = pdfs[0].filename
            for x in range(pages):
                pageparent = self.get_argument("pages[%d]['filename']" % x)
                pagenum = int(self.get_argument("pages[%d]['pagenum']" % x))
                rotation = int(
                    self.get_argument("pages[%d]['rotation']" % x) or 0)
                for name in bodies:
                    if name == pageparent:
                        page = PdfFileReader(
                            image2Pdf(bodies.get(name))).getPage(pagenum)
                        if rotation and rotation != 0:
                            method = ('rotateClockwise' if rotation > 0
                                      else 'rotateCounterClockwise')
                            getattr(page, method)(abs(rotation))
                        output.addPage(page)
            _file = BytesIO()
            output.write(_file)
            _file.seek(0)
            self.set_header('Content-Type', 'application/pdf')
            self.set_header('Content-Disposition',
                            'attachment; filename=%s' % filename)
            self.write(b64encode(_file.read()))


@url(r'/preview/')
class Preview(Route):
    def post(self):
        pdf = self.request.files.get('file', None)[0]
        if pdf.content_type != 'application/pdf':
            # It is maybe an image
            pdf = image2Pdf(pdf.body)
            pdf.body = pdf.read()
        _file = PdfFileReader(BytesIO(pdf.body))
        numpages = _file.getNumPages()
        output = {}
        for i in range(numpages):
            currpage = _file.getPage(i)
            writer = PdfFileWriter()
            writer.addPage(currpage)
            tmp = BytesIO()
            writer.write(tmp)
            tmp.seek(0)
            image = pdf2png(tmp, (300, 300))
            image.seek(0)
            output[i] = b64encode(image.read()).decode('utf-8')
        self.set_header("Content-Type", "application/json")
        return self.write(json_encode(output))


def image2Pdf(pdf):
    """Converts an image to a pdf and returns it's fd."""
    output = BytesIO()
    with Image(file=BytesIO(pdf)) as img:
        img.format = 'pdf'
        img.save(filename='/tmp/test.pdf')
        img.save(file=output)
    output.flush()
    output.seek(0)
    return output
