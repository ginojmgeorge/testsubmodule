import base
import logging
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


class PDFMaker:
    pagenum = True
    footer = None
    header = None
    invoiceformat = 0
    watermark = None
    topheight = 0
    provider = None

    def __init__(self, filename, **kwargs):
        self.pagesize = A4
        self.leftmargin = inch
        self.rightmargin = inch
        self.topmargin = inch
        self.bottommargin = inch
        self.title = None
        self.author = None
        self.subject = None
        self.creator = None
        self.producer = None
        self.keywords = []
        self.story = []
        self.doc = None
        self.width = 0
        self.height = 0
        for k in kwargs:
            if k in kwargs:
                v = kwargs[k]
            else:
                v = getattr(self, k)
            setattr(self, k, v)
        self.utility = base.Utility()
        self.open(filename)

    def open(self, filename):
        logging.getLogger("PIL").setLevel(logging.WARNING)
        self.doc = SimpleDocTemplate(filename, pagesize=self.pagesize, rightMargin=self.rightmargin, leftMargin=self.leftmargin, topMargin=self.topmargin, bottomMargin=self.bottommargin, title=self.title, author=self.author, subject=self.subject,
                                     creator=self.creator, producer=self.producer, keywords=[])

    def callback(self, canvas, doc):
        width, height = A4
        canvas.saveState()
        if PDFMaker.header is not None:
            self.width, self.height = PDFMaker.header.wrapOn(canvas, width, height)
            PDFMaker.header.drawOn(canvas, 40, 810 - self.height)
        if PDFMaker.footer is not None:
            if PDFMaker.provider is not None:
                if PDFMaker.provider is 'cloudoe':
                    self.width, self.height = PDFMaker.footer.wrapOn(canvas, width, height)
                    PDFMaker.footer.drawOn(canvas, 40, 100 - self.height)
            else:
                self.width, self.height = PDFMaker.footer.wrapOn(canvas, width, height)
                PDFMaker.footer.drawOn(canvas, 40, 70 - self.height)
        if PDFMaker.watermark is not None:
            canvas.rotate(45)
            self.width, self.height = PDFMaker.watermark.wrapOn(canvas, width, height)
            PDFMaker.watermark.drawOn(canvas, 250, 50)
        canvas.restoreState()

    def generate(self, story):
        if not base.nullorempty(PDFMaker.header) or not base.nullorempty(PDFMaker.footer) or not base.nullorempty(PDFMaker.watermark):
            self.doc.build(story, canvasmaker=base.UCanvas, onFirstPage=self.callback, onLaterPages=self.callback)
        else:
            self.doc.build(story, canvasmaker=base.UCanvas)
