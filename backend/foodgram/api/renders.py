import io
import os

from django.conf import settings
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether,
                                PageTemplate, Paragraph)
from rest_framework.renderers import BaseRenderer


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

        L = [Paragraph("Лист покупок", paragraph_style), ]

        for number, ingredient in enumerate(data):
            text = (f'__ {number+1}.'
                    f' {ingredient["ingredient__name"]}'
                    f' - {ingredient["total"]}'
                    f' {ingredient["ingredient__measurement_unit"]}')
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
