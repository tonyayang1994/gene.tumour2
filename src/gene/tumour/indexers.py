# -*- coding: utf-8 -*-
from logging import getLogger

from gene.tumour.interfaces import ITumour
from plone import api
from plone.app.contenttypes.indexers import SearchableText
from plone.app.contenttypes.indexers import _unicode_save_string_concat
from plone.indexer.decorator import indexer

logger = getLogger(__name__)


@indexer(ITumour)
def SearchableText_tumour(obj):
    return _unicode_save_string_concat(SearchableText(obj))


@indexer(ITumour)
def gid(obj):
    uuid = getattr(obj, 'gid', None)

    if uuid is None and getattr(obj, 'UID', None):
        return api.content.get_uuid(obj)
    return uuid
