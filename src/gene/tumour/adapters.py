# -*- coding: utf-8 -*-
import datetime

from gene.tumour.interfaces import ITumour
from plone.app.content.interfaces import INameFromTitle
from zope.component import adapter
from zope.interface import implementer


@implementer(INameFromTitle)
@adapter(ITumour)
class NameFromDatetime(object):
    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        now = datetime.datetime.now()
        title_id = str(now).translate(None, '- :.')
        return title_id
