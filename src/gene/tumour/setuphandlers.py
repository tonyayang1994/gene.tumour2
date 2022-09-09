# -*- coding: utf-8 -*-
import logging

from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.interfaces import constrains
from gene.tumour import _
from plone import api
from zope.interface import implementer
from zope.lifecycleevent import modified

logger = logging.getLogger(__name__)

PROFILE_ID = 'profile-gene.tumour:default'


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        return [
            'gene.tumour:uninstall',
        ]


def pre_handler(context):
    pass


def post_install(context):

    portal = api.portal.get()
    set_up_content(portal)


def uninstall(context):
    pass


def set_up_content(context):
    portal = api.portal.get()
    for item in STRUCTURE:
        _create_content(item, portal)


def _create_content(item_dict, container, force=False):
    if not force and container.get(item_dict['id'], None) is not None:
        return

    layout = item_dict.pop('layout', None)
    default_page = item_dict.pop('default_page', None)
    allowed_types = item_dict.pop('allowed_types', None)
    local_roles = item_dict.pop('local_roles', [])
    children = item_dict.pop('children', [])
    state = item_dict.pop('state', None)

    new = api.content.create(
        container=container,
        safe_id=True,
        **item_dict
    )
    logger.info('Created {0} at {1}'.format(new.portal_type,
                                            new.absolute_url()))

    if layout is not None:
        new.setLayout(layout)
    if default_page is not None:
        new.setDefaultPage(default_page)
    if allowed_types is not None:
        _constrain(new, allowed_types)
    for local_role in local_roles:
        api.group.grant_roles(
            groupname=local_role['group'],
            roles=local_role['roles'],
            obj=new)
    if state is not None:
        api.content.transition(new, to_state=state)

    modified(new)
    for subitem in children:
        _create_content(subitem, new)


def _constrain(context, allowed_types):
    behavior = constrains.ISelectableConstrainTypes(context)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setLocallyAllowedTypes(allowed_types)
    behavior.setImmediatelyAddableTypes(allowed_types)


STRUCTURE = [
    {
        'type': 'Folder',
        'title': u'Tumour',
        'id': 'tumour',
        'description': u'',
        'state': 'private',
        'layout': '@@genetumour-search-view',
        'allowed_types': ['Folder', 'Tumour'],
    },
]
