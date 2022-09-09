import logging

from gene.tumour import _
from plone import api
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform.form import AutoExtensibleForm
from z3c.form import button, form

logger = logging.getLogger(__name__)


class ChangeNoteForm(AutoExtensibleForm, form.EditForm):
    schema = IVersionable
    name = 'ChangeNoteForm'

    label = _(u"Add change notes")
    description = _(u"Add change notes, note the notes cannot be changed.")

    def update(self):
        self.request.set('disable_border', True)

        super(ChangeNoteForm, self).update()

    @button.buttonAndHandler(_(u'Save'))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        changes = {}
        if 'changeNote' in data and data['changeNote'] is not None and \
                len(data) == 1:
            obj = self.getContent()
            obj.description += data['changeNote'] + u'\n'
            changes = self.applyChanges(data)

        if changes:
            api.portal.show_message(
                _(u"Note has been added."), self.request, 'info')
        else:
            api.portal.show_message(
                _(u"Note has not been added."), self.request, 'warn')
        self.status = 'form status'
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        contextURL = self.context.absolute_url()
        self.request.response.redirect(contextURL)
