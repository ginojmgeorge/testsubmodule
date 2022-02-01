from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import base.pdfmaker


class UCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.pagenum = base.pdfmaker.PDFMaker.pagenum

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self.pagenum:
                self.drawfooter(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def drawfooter(self, page_count):
        page = "page %s of %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 8)
        self.setFillColorRGB(0.7, 0.7, 0.7)
        self.drawCentredString(105 * mm, 8 * mm, page)
