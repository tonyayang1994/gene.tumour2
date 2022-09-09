# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView


class AnalysisReportView(BrowserView):
    """"""

    def __init__(self, context, request):
        super(AnalysisReportView, self).__init__(context, request)
        self.items = []
