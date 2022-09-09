# -*- coding: utf-8 -*-
from plone.z3cform import layout

from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from gene.tumour.interfaces import IGeneTumourSettings
from gene.tumour import _


class GeneTumourControlPanelForm(RegistryEditForm):
    schema = IGeneTumourSettings

    label = _(u"Gene Tumour Settings")


GeneTumourControlPanelView = layout.wrap_form(
    GeneTumourControlPanelForm, ControlPanelFormWrapper)
