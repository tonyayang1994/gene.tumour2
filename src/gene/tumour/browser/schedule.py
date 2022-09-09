# -*- coding: utf-8 -*-
from gene.tumour.handlers import check_record_expiration
from zope.publisher.browser import BrowserView


class JobView(BrowserView):

    def __init__(self, context, request):
        super(JobView, self).__init__(context, request)

    def check_expiration_job(self):
        return check_record_expiration()
