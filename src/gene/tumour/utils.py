# -*- coding: utf-8 -*-


from gene.tumour import _
from gene.tumour.interfaces import IAnalysisResults
from gene.tumour.interfaces import IBloodSample
from gene.tumour.interfaces import IComputerDetecting
from gene.tumour.interfaces import ILibraryConstruction
from gene.tumour.interfaces import INAExtraction
from gene.tumour.interfaces import ITumour
from plone import api
from plone.memoize import forever
from zope.i18n import translate
from zope.schema import getFieldsInOrder


@forever.memoize
def fields():
    return getFieldsInOrder(ITumour)


@forever.memoize
def fields_name():
    return [field[0] for field in fields()]


@forever.memoize
def fields_title():
    request = api.portal.getRequest()
    return [translate(_(field[1].title), context=request)
            for field in fields()]

def export_fields_title():
    tmp = fields_title()
    tmp.append(u"状态")
    return tmp

review_states = [u'private', u'pending', u'success', u'failed', u'abort']
progress_steps = [u'step1', u'step2', u'step3', u'step4', u'step5']
normal_review_states = (u'private', u'pending', u'success',)

step1_len = len(IBloodSample.names()) - 1
step2_len = len(INAExtraction.names()) - 2
step3_len = len(ILibraryConstruction.names()) - 2
step4_len = len(IComputerDetecting.names()) - 2
step5_len = len(IAnalysisResults.names()) - 2

step1_start = 0
step1_end = step1_len
step2_start = step1_end
step2_end = step2_start + step2_len
step3_start = step2_end
step3_end = step3_start + step3_len
step4_start = step3_end
step4_end = step4_start + step4_len
step5_start = step4_end
step5_end = step5_start + step5_len

steps_start_end = ((step1_start, step1_end),
                   (step2_start, step2_end),
                   (step3_start, step3_end),
                   (step4_start, step4_end),
                   (step5_start, step5_end))

import_len = step1_len + step2_len + step3_len + step4_len
import_len = step1_len + step2_len + step3_len + step4_len + step5_len
