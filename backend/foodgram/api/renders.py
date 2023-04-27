from rest_framework.renderers import BaseRenderer
from io import BytesIO
import io
from reportlab.lib.pagesizes import letter, A5
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, KeepTogether
from reportlab.platypus import Frame, PageTemplate
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts
from django.conf import settings
import os


class ShoppingListToPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = '.pdf'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        buffer = io.BytesIO()

        font = ttfonts.TTFont('Arial', os.path.join(
            settings.STATIC_ROOT, 'fonts', 'arial.ttf'))
        pdfmetrics.registerFont(font)
        text_frame = Frame(
            x1=1.00 * cm,  # From left
            y1=1.0 * cm,  # From bottom
            height=19.0 * cm,
            width=12.8 * cm,
            leftPadding=1 * cm,
            bottomPadding=1 * cm,
            rightPadding=1 * cm,
            topPadding=1 * cm,
            showBoundary=1,
            id='text_frame')
        paragraph_style = ParagraphStyle(name='Normal',
                                         fontName='Arial',
                                         fontSize=24,
                                         leading=12,
                                         spaceBefore=20,
                                         spaceAfter=30)

        text_paragraph_style = ParagraphStyle(name='Normal',
                                              fontName='Arial',
                                              fontSize=14,
                                              leading=18,
                                              spaceBefore=12,
                                              spaceAfter=6)

        L = [Paragraph("Лист покупок", paragraph_style),]

        for number, ingredient in enumerate(data):
            text = f'__ {number+1}. {ingredient["ingredient__name"]} - {ingredient["total"]} {ingredient["ingredient__measurement_unit"]}'
            L.append(Paragraph(text, text_paragraph_style))

        story = L
        story.append(KeepTogether([]))
        doc = BaseDocTemplate(buffer, pagesize=A5)
        frontpage = PageTemplate(id='FrontPage',
                                 frames=[text_frame]
                                 )
        doc.addPageTemplates(frontpage)
        doc.build(story)
        buffer.seek(0)
        return buffer
