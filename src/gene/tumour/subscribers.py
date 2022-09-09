# -*- coding: utf-8 -*-
import logging

from gene.tumour import utils
from gene.tumour.interfaces import IStepsChangedEvent
from plone import api
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.textfield.value import RichTextValue
from zope.component import adapter

logger = logging.getLogger(__name__)


def set_gid(obj, event):
    gid = getattr(obj, 'gid', None)

    if gid is None:
        obj.gid = api.content.get_uuid(obj)
        obj.reindexObject(idxs=['gid'])


def set_title_text(obj, event):

    if obj.sample_no:
        title = unicode(obj.sample_no)
        if not title.startswith(u'SN'):
            title = u'SN: {0}'.format(title)
        obj.title = title

    field_value = []
    for name in utils.fields_name():
        field_value.append(unicode(getattr(obj, name, '')))

    if IRichText.providedBy(obj):
        text = u' '.join(map(unicode, field_value))
        rich_text = RichTextValue(
            text,
            'text/plain',
            'text/plain',
        )
        obj.text = rich_text

    obj.reindexObject(idxs=['title', 'SearchableText'])


@adapter(IStepsChangedEvent)
def steps_changed(event):
    logging.debug((event, event.object, event.oldSteps, event.newSteps))

